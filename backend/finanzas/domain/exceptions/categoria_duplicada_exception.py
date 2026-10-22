# finanzas/domain/exceptions/categoria_duplicada_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class CategoriaDuplicadaException(ValidacionException):
    campo = "nombre"
    mensaje = "Ya hay una categoría con ese nombre en este nivel."
