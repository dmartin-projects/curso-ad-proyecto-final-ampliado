# estadisticas/application/ports/i_reloj.py — qué día es hoy (módulo 89)
from abc import ABC, abstractmethod
from datetime import date


class IReloj(ABC):
    """La fecha de hoy: la del sistema en producción, una fija en los tests (como IReloj en el monolito)."""

    @abstractmethod
    def hoy(self) -> date: ...
