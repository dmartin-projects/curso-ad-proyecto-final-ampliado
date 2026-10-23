# usuarios/domain/exceptions/sesion_no_encontrada_exception.py — (módulo 92)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class SesionNoEncontradaException(NoEncontradoException):
    mensaje = "Esa sesión no existe o ya está cerrada."
