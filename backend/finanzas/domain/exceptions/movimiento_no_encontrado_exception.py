# finanzas/domain/exceptions/movimiento_no_encontrado_exception.py (módulo 87)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class MovimientoNoEncontradoException(NoEncontradoException):
    mensaje = "El movimiento no existe."
