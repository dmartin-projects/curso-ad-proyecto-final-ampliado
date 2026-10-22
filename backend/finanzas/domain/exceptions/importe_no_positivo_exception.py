# finanzas/domain/exceptions/importe_no_positivo_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class ImporteNoPositivoException(ValidacionException):
    campo = "importe"
    mensaje = "El importe debe ser mayor que cero."
