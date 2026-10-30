# asistente/domain/repositories/i_consumo_repository.py — el libro de cuentas del asistente (módulo 98)
from abc import ABC, abstractmethod
from collections.abc import Sequence

from asistente.domain.vo.consumo import Consumo


class IConsumoRepository(ABC):
    @abstractmethod
    def anotar(self, consumos: Sequence[Consumo]) -> None:
        """Solo se añade: un consumo no se cambia ni se borra (es lo que se ha pagado)."""
