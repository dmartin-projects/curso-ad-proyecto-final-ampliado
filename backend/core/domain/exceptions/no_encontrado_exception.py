# core/domain/exceptions/no_encontrado_exception.py (módulo 87)
from core.domain.exceptions.dominio_exception import DominioException


class NoEncontradoException(DominioException):
    """No existe… o no es de tu hogar: para quien pregunta, es lo mismo (módulo 36)."""

    codigo = "no_encontrado"
    status = 404
    mensaje = "El recurso no existe."
