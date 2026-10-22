# usuarios/domain/exceptions/email_ya_registrado_exception.py (módulos 35 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class EmailYaRegistradoException(ValidacionException):
    campo = "email"
    mensaje = "Ya hay una cuenta con ese email."
