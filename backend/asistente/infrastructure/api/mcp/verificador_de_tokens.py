# asistente/infrastructure/api/mcp/verificador_de_tokens.py — los tokens de Gastos, para el SDK de MCP (módulo 104)
from asgiref.sync import sync_to_async
from mcp.server.auth.provider import AccessToken

from oauth.domain.services.scopes import con_implicados
from oauth.infrastructure.api.authentication.token_de_recurso import verificar_token_de_recurso


class VerificadorDeTokensGastos:
    """El TokenVerifier del SDK (un Protocol): el SDK lo llama con el Bearer de cada petición y, si devuelve None,
    contesta 401 con el WWW-Authenticate que lleva al Protected Resource Metadata (RFC 9728). La comprobación es la de
    oauth (`verificar_token_de_recurso`): el token, su caducidad, la cuenta activa y el destinatario."""

    def __init__(self, recurso: str):
        self.recurso = recurso

    async def verify_token(self, token: str) -> AccessToken | None:
        t = await sync_to_async(verificar_token_de_recurso, thread_sensitive=True)(token, self.recurso)
        if t is None:
            return None
        return AccessToken(
            token=token,
            client_id=t.cliente_id,
            scopes=sorted(con_implicados(t.scopes)),  # gastos:escribir incluye gastos:leer
            expires_at=t.caduca,
            resource=t.recurso,  # con validate_token_resource, el SDK lo vuelve a comprobar: dos cerraduras
            subject=str(t.usuario_id),
        )
