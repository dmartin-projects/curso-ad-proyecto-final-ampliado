# oauth/domain/enums/tipo_cliente.py — qué aplicaciones pueden pedir tokens a Gastos, y con qué flujo (módulo 90)
#
# Tres tipos, y cada uno con UN flujo: así un cliente no puede usar un grant que no le corresponde.
#   NATIVA    CLI, app de escritorio o móvil. Public client: su código está en manos del usuario y no puede guardar
#             un secreto. Authorization code + PKCE; redirect a loopback (RFC 8252 §7.3).
#   WEB       Un backend con secreto (confidential client). Authorization code + PKCE (también: OAuth 2.1).
#   SERVICIO  Máquina a máquina, sin usuario: client credentials. Ni redirect ni scopes del usuario.
#   DISPOSITIVO  (ejercicio 3) Sin navegador cómodo (el CLI por SSH, una tele): device authorization grant (RFC 8628).
#             Public client, sin redirect. Solo la API: este flujo no emite ID tokens (no hay inicio de sesión EN
#             el dispositivo; la persona se identifica en su móvil u ordenador).
# Implicit y password no existen aquí: OAuth 2.1 y el RFC 9700 los retiran (y el servidor los rechaza igualmente).
from enum import StrEnum

from oauth.domain.services.scopes import DE_LA_API, DE_SERVICIO, DEL_USUARIO


class TipoCliente(StrEnum):
    NATIVA = "nativa"
    WEB = "web"
    SERVICIO = "servicio"
    DISPOSITIVO = "dispositivo"

    @property
    def confidencial(self) -> bool:
        return self in (TipoCliente.WEB, TipoCliente.SERVICIO)

    @property
    def con_usuario(self) -> bool:
        return self is not TipoCliente.SERVICIO

    @property
    def con_redirect(self) -> bool:
        """Los que vuelven al cliente por el navegador (authorization code)."""
        return self in (TipoCliente.NATIVA, TipoCliente.WEB)

    @property
    def scopes_permitidos(self) -> frozenset[str]:
        return {
            TipoCliente.NATIVA: DEL_USUARIO,
            TipoCliente.WEB: DEL_USUARIO,
            TipoCliente.SERVICIO: DE_SERVICIO,
            TipoCliente.DISPOSITIVO: DE_LA_API,
        }[self]
