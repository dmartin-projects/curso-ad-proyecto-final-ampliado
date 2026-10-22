# usuarios/domain/exceptions/contrasena_no_valida_exception.py (módulos 35 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class ContrasenaNoValidaException(ValidacionException):
    """La política de contraseñas puede dar varios motivos a la vez: van todos en errors.<campo>."""

    campo = "password"
    mensaje = "La contraseña no es válida."

    def __init__(self, mensajes: list[str], *, campo: str | None = None):
        super().__init__(" ".join(mensajes), campo=campo)
        self.mensajes = mensajes
