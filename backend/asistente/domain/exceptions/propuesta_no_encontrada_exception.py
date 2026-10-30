# asistente/domain/exceptions/propuesta_no_encontrada_exception.py (módulo 97)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class PropuestaNoEncontradaException(NoEncontradoException):
    """No existe, o es de otra persona u otro hogar: para quien pregunta, lo mismo (un 404)."""

    mensaje = "La propuesta no existe."
