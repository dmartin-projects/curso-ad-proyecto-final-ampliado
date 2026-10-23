# usuarios/domain/exceptions/contrasena_incorrecta_exception.py — (módulo 92)
from core.domain.exceptions.validacion_exception import ValidacionException


class ContrasenaIncorrectaException(ValidacionException):
    campo = "password"
    mensaje = "La contraseña no es correcta."
