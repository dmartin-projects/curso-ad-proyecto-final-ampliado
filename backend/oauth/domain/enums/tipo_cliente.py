# oauth/domain/enums/tipo_cliente.py — qué aplicaciones pueden pedir tokens a Gastos, y con qué flujo (módulo 90)
#
# Tres tipos, y cada uno con UN flujo: así un cliente no puede usar un grant que no le corresponde.
#   NATIVA    CLI, app de escritorio o móvil. Public client: su código está en manos del usuario y no puede guardar
#             un secreto. Authorization code + PKCE; redirect a loopback (RFC 8252 §7.3).
#   WEB       Un backend con secreto (confidential client). Authorization code + PKCE (también: OAuth 2.1).
#   SERVICIO  Máquina a máquina, sin usuario: client credentials. Ni redirect ni scopes del usuario.
# Implicit y password no existen aquí: OAuth 2.1 y el RFC 9700 los retiran (y el servidor los rechaza igualmente).
from enum import StrEnum


class TipoCliente(StrEnum):
    NATIVA = "nativa"
    WEB = "web"
    SERVICIO = "servicio"

    @property
    def confidencial(self) -> bool:
        return self is not TipoCliente.NATIVA

    @property
    def con_usuario(self) -> bool:
        return self is not TipoCliente.SERVICIO
