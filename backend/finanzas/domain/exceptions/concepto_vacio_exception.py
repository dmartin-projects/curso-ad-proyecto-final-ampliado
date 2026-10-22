# finanzas/domain/exceptions/concepto_vacio_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class ConceptoVacioException(ValidacionException):
    campo = "concepto"
    mensaje = "El concepto no puede estar vacío."
