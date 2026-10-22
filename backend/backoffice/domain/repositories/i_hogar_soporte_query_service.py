# backoffice/domain/repositories/i_hogar_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.hogar_soporte import HogarSoporte
from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery
from core.domain.read_models.pagina import Pagina


class IHogarSoporteQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoSoporteQuery) -> Pagina[HogarSoporte]:
        """Con sus contadores (miembros y movimientos), sin N+1."""

    @abstractmethod
    def detalle(self, hogar_id: int) -> HogarSoporte | None:
        """Con sus miembros."""
