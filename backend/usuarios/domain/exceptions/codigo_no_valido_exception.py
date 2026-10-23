# usuarios/domain/exceptions/codigo_no_valido_exception.py — (módulo 92)
from core.domain.exceptions.validacion_exception import ValidacionException


class CodigoNoValidoException(ValidacionException):
    campo = "codigo"
    mensaje = "El código no es correcto o ya se ha usado."
