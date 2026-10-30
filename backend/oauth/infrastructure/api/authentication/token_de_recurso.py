# oauth/infrastructure/api/authentication/token_de_recurso.py — un access token de Gastos para UN recurso (módulo 104)
#
# Para los resource servers que no son la API de DRF (el servidor MCP del asistente): la misma comprobación que
# AutenticacionOAuth, más la del destinatario. Un token sirve para el recurso que se pidió con `resource` (RFC 8707) al
# autorizar, y para nada más; un token sin recurso (los de la API, los de gastos-cli) aquí no vale.
import hashlib
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from oauth2_provider.models import get_access_token_model

from oauth.infrastructure.server.generadores_de_tokens import PREFIJO_ACCESS


@dataclass(frozen=True, slots=True)
class TokenDeRecurso:
    usuario_id: int
    cliente_id: str
    scopes: frozenset[str]
    recurso: str
    caduca: int  # epoch, en segundos


PUERTOS = {"http": 80, "https": 443}


def canonica(uri: str) -> str:
    """La forma canónica de una URI de recurso (RFC 3986 §6.2.2-6.2.3): esquema y host en minúsculas, sin el puerto por
    defecto y sin la barra final. La ruta, tal cual: /api/MCP es otro recurso."""
    try:
        partes = urlsplit(uri.strip())
        puerto = partes.port
    except ValueError:
        return uri
    esquema, host = partes.scheme.lower(), (partes.hostname or "")
    netloc = host if puerto in (None, PUERTOS.get(esquema)) else f"{host}:{puerto}"
    return urlunsplit((esquema, netloc, partes.path.rstrip("/"), partes.query, ""))


def verificar_token_de_recurso(token: str, recurso: str) -> TokenDeRecurso | None:
    """None si el token no existe, ha caducado o se ha revocado, no es de una persona (client credentials), su cuenta
    está desactivada o no se emitió para `recurso`. El mismo None en todos los casos: quien prueba tokens no aprende
    nada de la respuesta."""
    if not token.startswith(PREFIJO_ACCESS):
        return None
    checksum = hashlib.sha256(token.encode()).hexdigest()  # en la base de datos, solo el hash (RFC 9700)
    access = (
        get_access_token_model().objects.select_related("application", "user").filter(token_checksum=checksum).first()
    )
    if access is None or not access.is_valid() or access.user is None or not access.user.is_active:
        return None
    # El recurso EXACTO: no el prefijo que DOT acepta por defecto en la API, con el que un token pedido para
    # "https://api.gastos.…/" valdría también para "…/mcp". MCP pide tokens emitidos para el servidor. Exacto después de
    # normalizar lo que no cambia la URI (MCP: «SHOULD accept uppercase scheme and host»)
    if canonica(recurso) not in {canonica(r) for r in access.resource or []}:
        return None
    return TokenDeRecurso(
        usuario_id=access.user_id,
        cliente_id=access.application.client_id,
        scopes=frozenset(access.scope.split()),
        recurso=recurso,
        caduca=int(access.expires.timestamp()),
    )
