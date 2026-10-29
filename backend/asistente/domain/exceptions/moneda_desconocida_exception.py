# asistente/domain/exceptions/moneda_desconocida_exception.py (módulo 95)
from core.domain.exceptions.validacion_exception import ValidacionException


class MonedaDesconocidaException(ValidacionException):
    codigo = "moneda_desconocida"
    mensaje = "Esa moneda no la publica el Banco Central Europeo. Usa un código ISO 4217 de tres letras (GBP, USD…)."
