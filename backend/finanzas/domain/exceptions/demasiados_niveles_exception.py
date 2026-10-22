# finanzas/domain/exceptions/demasiados_niveles_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class DemasiadosNivelesException(ValidacionException):
    campo = "padre"
    mensaje = "Solo se permiten dos niveles de categorías."
