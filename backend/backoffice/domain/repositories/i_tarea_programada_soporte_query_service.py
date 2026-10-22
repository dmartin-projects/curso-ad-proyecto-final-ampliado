# backoffice/domain/repositories/i_tarea_programada_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.tarea_programada_soporte import TareaProgramadaSoporte


class ITareaProgramadaSoporteQueryService(ABC):
    @abstractmethod
    def listar(self) -> list[TareaProgramadaSoporte]:
        """Todas, por nombre (no se paginan: son unas pocas)."""

    @abstractmethod
    def detalle(self, tarea_id: int) -> TareaProgramadaSoporte | None: ...
