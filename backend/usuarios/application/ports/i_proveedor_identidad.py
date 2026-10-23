# usuarios/application/ports/i_proveedor_identidad.py — un proveedor de identidad: Google, GitHub, Apple… (módulos 91 y 92)
from abc import ABC, abstractmethod

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial


class IProveedorIdentidad(ABC):
    """Un proveedor de identidad (Google, GitHub, Apple…). El adapter habla su protocolo (OIDC u OAuth 2.0) y devuelve
    un perfil ya comprobado: los tokens del proveedor no salen de él (ni a la SPA ni a la base de datos)."""

    proveedor: Proveedor
    modo_respuesta: str | None = None  # cómo vuelve el navegador: en la query (None) o con un POST ("form_post")
    reautentica: bool = (
        False  # módulo 92, ej. 3: puede volver a pedir la contraseña y decir cuándo (max_age, auth_time)
    )

    @abstractmethod
    def url_de_autorizacion(self, transaccion: TransaccionSocial) -> str:
        """Adónde mandar el navegador: el authorization endpoint con state, nonce y, si lo admite, PKCE."""

    @abstractmethod
    def completar(self, transaccion: TransaccionSocial, parametros: dict[str, str]) -> PerfilExterno:
        """`parametros`: los de la vuelta (el code; en Apple, también `user`). Canjea el code y comprueba la respuesta.
        Si algo no cuadra: LoginSocialNoValidoException."""
