# asistente/domain/repositories/i_recuerdo_query_service.py (módulo 99)
from abc import ABC, abstractmethod

from asistente.domain.read_models.recuerdo_listado import RecuerdoListado


class IRecuerdoQueryService(ABC):
    @abstractmethod
    def listar(self, usuario_id: int, hogar_id: int) -> tuple[RecuerdoListado, ...]:
        """Los de esa persona en ese hogar, del más antiguo al más nuevo (el orden en que viajan)."""
