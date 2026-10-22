# usuarios/domain/exceptions/email_no_valido_exception.py (módulos 35 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class EmailNoValidoException(ValidacionException):
    campo = "email"
    mensaje = "Introduce un email válido."
