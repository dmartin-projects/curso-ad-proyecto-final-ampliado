# finanzas/domain/exceptions/fecha_futura_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class FechaFuturaException(ValidacionException):
    campo = "fecha"
    mensaje = "La fecha no puede ser futura."
