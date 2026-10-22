# oauth/domain/exceptions/redirect_uri_no_valida_exception.py (módulo 90)
from core.domain.exceptions.validacion_exception import ValidacionException


class RedirectUriNoValidaException(ValidacionException):
    campo = "redirect_uris"
    mensaje = "Redirect URI no válida."
