# core/application/ports/i_reloj.py (módulo 87)
from abc import ABC, abstractmethod
from datetime import date


class IReloj(ABC):
    """Qué día es hoy. En Django, la fecha en la zona horaria del proyecto; en los tests, una fecha fija."""

    @abstractmethod
    def hoy(self) -> date: ...
