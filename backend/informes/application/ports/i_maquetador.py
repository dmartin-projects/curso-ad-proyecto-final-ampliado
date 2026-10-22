# informes/application/ports/i_maquetador.py — el PDF del mes (módulo 88)
from abc import ABC, abstractmethod

from core.domain.vo.mes import Mes


class IMaquetador(ABC):
    """El PDF del mes: los mismos números que el dashboard y los movimientos agrupados por categoría."""

    @abstractmethod
    def pdf(self, hogar_id: int, mes: Mes, idioma: str | None = None) -> bytes: ...
