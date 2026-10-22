# oauth/domain/exceptions/cliente_ya_existe_exception.py (módulo 90)
from core.domain.exceptions.validacion_exception import ValidacionException


class ClienteYaExisteException(ValidacionException):
    campo = "client_id"
    mensaje = "Ya hay un cliente con ese client_id."
