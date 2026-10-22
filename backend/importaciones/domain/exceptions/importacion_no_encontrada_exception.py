# importaciones/domain/exceptions/importacion_no_encontrada_exception.py (módulos 75 y 88)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class ImportacionNoEncontradaException(NoEncontradoException):
    mensaje = "La importación no existe."
