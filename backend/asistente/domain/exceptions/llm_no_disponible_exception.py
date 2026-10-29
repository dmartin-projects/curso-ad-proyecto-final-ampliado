# asistente/domain/exceptions/llm_no_disponible_exception.py — 429, 5xx, timeout, red (módulo 93)
from asistente.domain.exceptions.llm_exception import LLMException


class LLMNoDisponibleException(LLMException):
    """Transitorio: más tarde, o con otro modelo (módulo 94), puede funcionar.

    `reintentar_en`: los segundos que pide el proveedor (cabecera retry-after de un 429), si los dice. Con una cuota
    por minuto son segundos; con la diaria, horas: reintentar sin mirarlo es perder el tiempo.
    """

    def __init__(self, mensaje: str, reintentar_en: float | None = None):
        super().__init__(mensaje)
        self.reintentar_en = reintentar_en
