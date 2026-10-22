# finanzas/domain/exceptions/importe_cero_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class ImporteCeroException(ValidacionException):
    campo = "importe"
    mensaje = "El importe no puede ser cero."
