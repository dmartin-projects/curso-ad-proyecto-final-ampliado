# hogares/domain/repositories/i_miembro_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from core.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from hogares.domain.read_models.miembro_listado import MiembroListado


class IMiembroQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoDelHogarQuery) -> list[MiembroListado]:
        """Los miembros del hogar con su usuario, por antigüedad si no se pide otro orden."""

    @abstractmethod
    def detalle(self, hogar_id: int, membresia_id: int) -> MiembroListado | None: ...
