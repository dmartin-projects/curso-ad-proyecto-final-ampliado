# informes/domain/exceptions/mes_futuro_exception.py (módulos 78 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class MesFuturoException(ValidacionException):
    campo = "mes"
    mensaje = "No se puede generar el informe de un mes futuro."
