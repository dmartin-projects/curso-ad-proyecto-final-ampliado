# asistente/infrastructure/api/mcp/aplicacion_mcp.py — el servidor MCP como aplicación ASGI (módulo 104)
"""El SDK monta, para un Server, una app de Starlette con dos rutas:

    POST /api/mcp                                        el protocolo (Streamable HTTP), detrás del Bearer
    GET  /.well-known/oauth-protected-resource/api/mcp   el Protected Resource Metadata (RFC 9728): quién emite
                                                         los tokens para este recurso y con qué scopes

y config/asgi.py le pasa esas rutas; el resto sigue yendo a Django. Bajo /api, como toda la API: en producción llega
por Vercel (módulo 86), en el mismo origen que el authorization server (/api/oauth).

STATELESS (sin sesión del lado del servidor) y con respuestas JSON: con el protocolo de 2026-07-28 cada petición se
basta a sí misma, así que cualquier worker de gunicorn puede contestarla (ni sesiones pegajosas en Caddy ni estado
compartido). El gestor del SDK necesita un "lifespan" que lo arranque; aquí, uno por petición: así funciona igual con
uvicorn (producción) que con daphne (runserver, E2E), que no tiene lifespan.

Fuera de Django, lo que su ASGIHandler hace en cada petición hay que hacerlo a mano:
- un ThreadSensitiveContext: sync_to_async(thread_sensitive=True) (los tokens, las tools) usa el hilo de ESTA petición.
  Sin él, todas las peticiones MCP del proceso comparten un único hilo y una tool lenta pone en fila a las demás;
- close_old_connections al empezar y al acabar: una conexión a PostgreSQL rota (un reinicio, un failover) o pasada de
  CONN_MAX_AGE se cierra y la siguiente consulta abre otra. Sin esto, el servidor MCP contestaría 500 hasta reiniciar.

Y las cabeceras WWW-Authenticate del SDK, ajustadas a RFC 6750 §3.1 y a MCP: sin credenciales, el 401 no lleva código
de error (no ha habido un token que esté mal); y el 401 y el 403 dicen qué scope hace falta.
"""

import json
from collections.abc import Callable

from asgiref.sync import ThreadSensitiveContext, sync_to_async
from django.db import close_old_connections
from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings

from asistente.infrastructure.api.mcp.limite_de_llamadas import LimiteDeLlamadas
from asistente.infrastructure.api.mcp.servidor_mcp import SCOPE, ServidorMCP
from asistente.infrastructure.api.mcp.verificador_de_tokens import VerificadorDeTokensGastos

RUTA = "/api/mcp"
METADATA = "/.well-known/oauth-protected-resource/api/mcp"


class AplicacionMCP:
    def __init__(
        self,
        servidor: ServidorMCP,
        *,
        recurso: str,
        emisor: str,
        hosts: list[str],
        origenes: list[str],
        apagado: Callable[[], str | None] = lambda: None,
    ):
        """`recurso`: la URI canónica del servidor (https://gastos.…/api/mcp), la que los clientes piden con `resource` y la
        que tiene que llevar el token; `emisor`: el authorization server (OAUTH_ISSUER, módulo 90). Módulo 107:
        `apagado()` → el mensaje si quien opera la app ha apagado el asistente (None si no)."""
        self.servidor, self.apagado = servidor, apagado
        self.auth = AuthSettings(
            issuer_url=emisor,
            resource_server_url=recurso,
            required_scopes=[SCOPE],
            validate_token_resource=True,
        )
        self.verificador = VerificadorDeTokensGastos(recurso)
        # DNS rebinding: solo los Host de la API, y los Origin de la app (un navegador que llama desde otra web, no)
        self.seguridad = TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=origenes)

    @staticmethod
    def atiende(ruta: str) -> bool:
        return ruta in (RUTA, f"{RUTA}/", METADATA)

    async def __call__(self, scope, receive, send):
        # Módulo 107: el interruptor apaga también lo que el asistente ofrece a otros clientes (las mismas tools)
        if scope["path"] != METADATA and (mensaje := await sync_to_async(self.apagado)()):
            return await _no_disponible(send, mensaje)
        app = self.servidor.servidor.streamable_http_app(
            streamable_http_path=RUTA,
            stateless_http=True,
            json_response=True,
            transport_security=self.seguridad,
            auth=self.auth,
            token_verifier=self.verificador,
        )
        async with ThreadSensitiveContext():
            await sync_to_async(close_old_connections)()
            try:
                async with app.router.lifespan_context(app):
                    await app(scope, receive, _con_desafio(scope, send))
            finally:
                await sync_to_async(close_old_connections)()


async def _no_disponible(send, mensaje: str) -> None:
    cuerpo = json.dumps({"detail": mensaje}, ensure_ascii=False).encode()
    cabeceras = [(b"content-type", b"application/json"), (b"retry-after", b"300")]
    await send({"type": "http.response.start", "status": 503, "headers": cabeceras})
    await send({"type": "http.response.body", "body": cuerpo})


def _con_desafio(scope, send):
    """El `send` de la petición, con el WWW-Authenticate de los 401 y 403 corregido (ver arriba)."""
    sin_credenciales = not any(
        k.lower() == b"authorization" and v[:7].lower() == b"bearer " for k, v in scope.get("headers", [])
    )

    async def enviar(mensaje):
        if mensaje["type"] == "http.response.start" and mensaje["status"] in (401, 403):
            quitar_error = mensaje["status"] == 401 and sin_credenciales
            mensaje = {
                **mensaje,
                "headers": [
                    (k, desafio(v.decode(), quitar_error).encode() if k.lower() == b"www-authenticate" else v)
                    for k, v in mensaje["headers"]
                ],
            }
        await send(mensaje)

    return enviar


def desafio(cabecera: str, quitar_error: bool) -> str:
    """'Bearer error="…", error_description="…", resource_metadata="…"' → con scope="gastos:leer" y, si no venían
    credenciales, sin error ni error_description."""
    partes = [p.strip() for p in cabecera.removeprefix("Bearer ").split(", ") if p.strip()]
    if quitar_error:
        partes = [p for p in partes if not p.startswith(("error=", "error_description="))]
    return "Bearer " + ", ".join([*partes, f'scope="{SCOPE}"'])


def crear_aplicacion_mcp() -> AplicacionMCP:
    """El adapter de entrada pide las piezas al container (como las views de la API): las tools de consulta, el
    contexto de una pregunta y los hogares de una persona."""
    from django.conf import settings

    from asistente.infrastructure import container

    servidor = ServidorMCP(
        tools=container.tools(),
        contexto=container.contexto,
        hogares=container.hogares_de,
        limite=LimiteDeLlamadas(settings.ASISTENTE_MCP_LLAMADAS_POR_MINUTO).espera,  # ejercicio 1
        al_llamar=container.contar_llamada_mcp,  # ejercicio 3
    )
    hosts = [*settings.ALLOWED_HOSTS, *(f"{h}:*" for h in settings.ALLOWED_HOSTS)]
    return AplicacionMCP(
        servidor,
        recurso=settings.ASISTENTE_MCP_URL,
        emisor=settings.OAUTH_ISSUER,
        hosts=hosts,
        origenes=[settings.FRONTEND_URL],
        apagado=_apagado,
    )


def _apagado() -> str | None:
    """Módulo 107: solo el interruptor (ASISTENTE_ACTIVO). Sin modelos (Groq caído), las tools siguen sirviendo: no
    llaman a ningún modelo."""
    from asistente.domain.exceptions.asistente_no_disponible_exception import AsistenteNoDisponibleException
    from asistente.domain.vo.estado_del_asistente import APAGADO
    from asistente.infrastructure import container

    if container.estado_del_asistente().estado().motivo == APAGADO:
        return AsistenteNoDisponibleException(APAGADO).mensaje
    return None
