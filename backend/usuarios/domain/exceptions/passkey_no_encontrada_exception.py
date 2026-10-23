# usuarios/domain/exceptions/passkey_no_encontrada_exception.py — (módulo 92)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class PasskeyNoEncontradaException(NoEncontradoException):
    mensaje = "Esa passkey no existe."
