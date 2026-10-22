# core/application/ports/i_reloj.py (módulos 87 y 88)
from abc import ABC, abstractmethod
from datetime import date, datetime


class IReloj(ABC):
    """Qué día es hoy y qué hora es. En Django, los de la zona horaria del proyecto; en los tests, fijos."""

    @abstractmethod
    def hoy(self) -> date: ...

    @abstractmethod
    def ahora(self) -> datetime:
        """Con zona horaria (aware): caducidades, fechas de proceso, marcas de publicación (módulo 88)."""
