# asistente/domain/exceptions/grafico_no_encontrado_exception.py (módulo 97)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class GraficoNoEncontradoException(NoEncontradoException):
    """No existe, o es de otra persona u otro hogar: para quien pregunta, lo mismo (un 404)."""

    mensaje = "El gráfico no existe."
