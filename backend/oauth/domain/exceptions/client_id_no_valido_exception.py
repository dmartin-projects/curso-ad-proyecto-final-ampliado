# oauth/domain/exceptions/client_id_no_valido_exception.py (módulo 90)
from core.domain.exceptions.validacion_exception import ValidacionException


class ClientIdNoValidoException(ValidacionException):
    campo = "client_id"
    mensaje = "El client_id solo puede tener letras, cifras, puntos, guiones y guiones bajos (de 3 a 100)."
