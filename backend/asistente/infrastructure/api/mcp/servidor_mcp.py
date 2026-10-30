# asistente/infrastructure/api/mcp/servidor_mcp.py — el servidor MCP de Gastos (módulo 104)
"""Las tools de CONSULTA del asistente, para cualquier cliente MCP (un IDE, un agente de escritorio, otro agente),
con el protocolo de 2026-07-28 sobre Streamable HTTP y la autorización OAuth 2.1 de Gastos (módulo 90).

Es un adapter de ENTRADA, como la API REST: recibe una petición, saca quién es del token, monta el ContextoPregunta y
ejecuta la misma Tool que usa el agente. Lo que puede hacer cada llamada es la INTERSECCIÓN de tres cosas:

    el rol de la persona en el hogar  ∩  el techo de los scopes del token  ∩  LECTOR (el agente solo lee)

El hogar va en los argumentos (a diferencia del chat, donde va en la URL de la sesión): quien llama es un cliente que
actúa por la persona, y la persona puede pedir cualquiera de SUS hogares. Si no es miembro, el mismo error exista o no.
Solo las tools de consulta: proponer un movimiento necesita la tarjeta de confirmación del chat.
"""

import json
import logging
import time
from dataclasses import replace
from traceback import format_tb

import mcp_types as types
from asgiref.sync import sync_to_async
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.lowlevel import Server

from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.tool import Tool
from asistente.domain.exceptions.tool_exception import ToolException
from core.domain.enums.rol import Rol
from core.domain.exceptions.dominio_exception import DominioException
from oauth.domain.services.scopes import techo

logger = logging.getLogger(__name__)
SCOPE = "gastos:leer"
HOGAR = {"type": "integer", "description": "El id del hogar (listar_hogares). Solo los tuyos."}
LISTAR_HOGARES = types.Tool(
    name="listar_hogares",
    description="Los hogares de la persona: id, nombre, moneda y su rol. Llámala antes que las demás.",
    input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    annotations=types.ToolAnnotations(read_only_hint=True, open_world_hint=False),
)


def declaracion_mcp(tool: Tool) -> types.Tool:
    """La declaración de una tool del agente, con el hogar como argumento obligatorio."""
    d = tool.declaracion()
    esquema = dict(d.parametros)
    esquema["properties"] = {"hogar": HOGAR, **esquema.get("properties", {})}
    esquema["required"] = ["hogar", *esquema.get("required", [])]
    return types.Tool(
        name=d.nombre,
        description=d.descripcion,
        input_schema=esquema,
        annotations=types.ToolAnnotations(read_only_hint=True, open_world_hint=False),
    )


class ServidorMCP:
    def __init__(self, *, tools: list[Tool], contexto, hogares, limite=None, al_llamar=None):
        """`contexto(usuario_id, hogar_id)` → ContextoPregunta (o SinPermisoException); `hogares(usuario_id)` → los
        hogares de la persona. Del container: aquí no se elige ningún adapter.

        Ejercicio 1: `limite(cliente, usuario)` → segundos que esperar (0: puede). Ejercicio 3: `al_llamar(cliente, tool,
        error)`, para la métrica."""
        self.tools = {t.nombre: t for t in tools}
        self.contexto, self.hogares = contexto, hogares
        self.limite, self.al_llamar = limite, al_llamar
        self.servidor = Server(
            "gastos",
            title="Gastos",
            description="Los gastos de tus hogares: resúmenes, categorías, movimientos, presupuestos.",
            on_list_tools=self._listar,
            on_call_tool=self._llamar,
        )

    async def _listar(self, ctx, params) -> types.ListToolsResult:
        return types.ListToolsResult(tools=[LISTAR_HOGARES, *(declaracion_mcp(t) for t in self.tools.values())])

    async def _llamar(self, ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
        token = get_access_token()  # el middleware de autenticación del SDK ya lo ha comprobado
        if token is None or SCOPE not in token.scopes:  # (con required_scopes no pasa; si se quitan, que no se abra)
            return _error(f"Hace falta el scope {SCOPE}.")
        if self.limite is not None and (espera := await sync_to_async(self.limite)(token.client_id, token.subject)):
            # Un resultado con is_error: el modelo del cliente lo lee y espera (un 429 del transporte lo reintentaría
            # el SDK sin que nadie lo vea). No se ejecuta nada
            if self.al_llamar is not None:
                self.al_llamar(token.client_id, params.name, "limite")
            return _error(f"Demasiadas llamadas. Vuelve a intentarlo dentro de {espera} s.")
        inicio = time.monotonic()
        resultado = await sync_to_async(self._ejecutar, thread_sensitive=True)(
            int(token.subject), frozenset(token.scopes), params.name, dict(params.arguments or {})
        )
        logger.info(
            "MCP: %s %s",
            params.name,
            "error" if resultado.is_error else "ok",
            extra={"mcp": {"cliente": token.client_id, "usuario_id": token.subject, "tool": params.name,
                           "error": resultado.is_error, "ms": int((time.monotonic() - inicio) * 1000)}},
        )  # fmt: skip
        if self.al_llamar is not None:
            self.al_llamar(token.client_id, params.name, "error" if resultado.is_error else "ok")
        return resultado

    def _ejecutar(self, usuario_id: int, scopes: frozenset[str], nombre: str, args: dict) -> types.CallToolResult:
        if nombre == "listar_hogares":
            return _ok({"hogares": self.hogares(usuario_id)})
        tool = self.tools.get(nombre)
        if tool is None:
            return _error(f"La tool '{nombre}' no existe. Las que hay: listar_hogares, {', '.join(self.tools)}.")
        hogar = args.pop("hogar", None)
        if not isinstance(hogar, int) or isinstance(hogar, bool):
            return _error("Falta el argumento 'hogar' (un número: el id que da listar_hogares).")
        try:
            contexto = self.contexto(usuario_id, hogar)
            # Rol en el hogar ∩ techo de los scopes (∩ LECTOR, que ya pone ContextoPregunta)
            contexto = replace(contexto, actor=contexto.actor.limitado_a(techo(scopes) or Rol.LECTOR))
            contenido = tool.ejecutar(contexto, tool.validar(json.dumps(args)))
        except ToolException as e:
            return _error(str(e))
        except DominioException as e:  # sin permiso, un dato que no existe: su mensaje es público
            return _error(e.mensaje)
        except Exception as e:  # como en el agente (módulo 94): sin los argumentos ni el mensaje, que llevan datos
            logger.error(
                "Error en la tool %s por MCP: %s\n%s", nombre, type(e).__name__, "".join(format_tb(e.__traceback__))
            )
            return _error(f"Error interno en {nombre}.")
        if isinstance(contenido, ConArtefacto):
            contenido = contenido.para_el_modelo
        return _ok(contenido)


def _ok(datos: dict) -> types.CallToolResult:
    texto = json.dumps(datos, ensure_ascii=False, default=str)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=texto)], structured_content=json.loads(texto)
    )


def _error(mensaje: str) -> types.CallToolResult:
    # Un error de la tool es un RESULTADO (is_error) que el modelo del cliente lee y corrige, no un error del protocolo
    return types.CallToolResult(content=[types.TextContent(type="text", text=mensaje)], is_error=True)
