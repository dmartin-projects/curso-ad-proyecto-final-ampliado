# usuarios/domain/exceptions/contrasena_actual_incorrecta_exception.py (módulos 35 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class ContrasenaActualIncorrectaException(ValidacionException):
    campo = "actual"
    mensaje = "La contraseña actual no es correcta."
