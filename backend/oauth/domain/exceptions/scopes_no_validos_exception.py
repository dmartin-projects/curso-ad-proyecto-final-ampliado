# oauth/domain/exceptions/scopes_no_validos_exception.py (módulo 90)
from core.domain.exceptions.validacion_exception import ValidacionException


class ScopesNoValidosException(ValidacionException):
    campo = "scopes"
    mensaje = "Scopes no válidos para este tipo de cliente."
