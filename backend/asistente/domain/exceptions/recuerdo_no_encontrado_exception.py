# asistente/domain/exceptions/recuerdo_no_encontrado_exception.py (módulo 99)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class RecuerdoNoEncontradoException(NoEncontradoException):
    mensaje = "Ese recuerdo no existe."
