# finanzas/domain/exceptions/presupuesto_duplicado_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class PresupuestoDuplicadoException(ValidacionException):
    campo = "categoria"
    mensaje = "Ya hay un presupuesto de esta categoría para ese mes."
