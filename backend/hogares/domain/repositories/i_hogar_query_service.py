# hogares/domain/repositories/i_hogar_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from core.domain.read_models.pagina import Pagina
from hogares.domain.read_models.hogar_listado import HogarListado
from hogares.domain.repositories.queries.hogares_query import HogaresQuery


class IHogarQueryService(ABC):
    @abstractmethod
    def listar(self, query: HogaresQuery) -> Pagina[HogarListado]:
        """Los hogares de la persona con su rol en cada uno y cuántos miembros tiene (una consulta)."""

    @abstractmethod
    def detalle(self, usuario_id: int, hogar_id: int) -> HogarListado | None:
        """El hogar si la persona es miembro; si no, None (para ella no existe)."""
