# core/domain/exceptions/pagina_no_valida_exception.py (módulo 87)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class PaginaNoValidaException(NoEncontradoException):
    mensaje = "La página no existe."
