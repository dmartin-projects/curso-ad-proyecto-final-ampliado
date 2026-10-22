# estadisticas/domain/repositories/i_progreso_query_service.py — el lado de LECTURA (CQRS, módulo 89)
from abc import ABC, abstractmethod
from datetime import datetime


class IProgresoQueryService(ABC):
    @abstractmethod
    def ultimo_evento(self) -> datetime | None:
        """Cuándo se publicó el último cambio que ya está aplicado (None si no hay ninguno)."""
