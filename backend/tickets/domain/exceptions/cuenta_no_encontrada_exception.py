# tickets/domain/exceptions/cuenta_no_encontrada_exception.py (módulos 74 y 88)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class CuentaNoEncontradaException(NoEncontradoException):
    campo = "cuenta"
    mensaje = "La cuenta no existe en este hogar."
