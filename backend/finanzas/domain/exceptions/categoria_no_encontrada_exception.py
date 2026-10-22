# finanzas/domain/exceptions/categoria_no_encontrada_exception.py (módulo 87)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class CategoriaNoEncontradaException(NoEncontradoException):
    mensaje = "La categoría no existe en este hogar."
