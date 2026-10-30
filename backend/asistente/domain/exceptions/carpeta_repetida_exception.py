# asistente/domain/exceptions/carpeta_repetida_exception.py (módulo 97)
from core.domain.exceptions.validacion_exception import ValidacionException


class CarpetaRepetidaException(ValidacionException):
    mensaje = "Ya tienes una carpeta con ese nombre."
    campo = "nombre"
