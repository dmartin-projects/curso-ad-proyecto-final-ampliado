# usuarios/domain/vo/perfil_externo.py — quién dice el proveedor que es la persona (módulo 91)
from dataclasses import dataclass

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.email_no_valido_exception import EmailNoValidoException
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.services.emails import normalizar_email


@dataclass(frozen=True, slots=True)
class PerfilExterno:
    """Quién dice el proveedor que es la persona, ya comprobado por el adapter (firma, iss, aud, nonce…).

    La identidad es (proveedor, sub): el `sub` es estable y no se reasigna. El email puede cambiar, repetirse en otro
    proveedor o no estar verificado: es un dato, nunca la clave.
    """

    proveedor: Proveedor
    sub: str
    email: str | None = None
    email_verificado: bool = False
    nombre: str = ""
    apellidos: str = ""

    def __post_init__(self):
        if not self.sub:
            raise LoginSocialNoValidoException("El proveedor no ha dicho quién eres.")
        if self.email is not None:
            try:
                object.__setattr__(self, "email", normalizar_email(self.email))
            except EmailNoValidoException:  # un email que no es un email no sirve para nada: como si no lo hubiera
                object.__setattr__(self, "email", None)
                object.__setattr__(self, "email_verificado", False)
