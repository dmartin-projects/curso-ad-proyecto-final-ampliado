# core/domain/exceptions/cursor_no_valido_exception.py (módulo 87)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class CursorNoValidoException(NoEncontradoException):
    mensaje = "El cursor no es válido."
