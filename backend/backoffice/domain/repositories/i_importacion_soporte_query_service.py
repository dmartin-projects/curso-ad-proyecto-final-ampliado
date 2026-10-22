# backoffice/domain/repositories/i_importacion_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.importacion_soporte import ImportacionSoporte
from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery
from core.domain.read_models.pagina import Pagina


class IImportacionSoporteQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoSoporteQuery) -> Pagina[ImportacionSoporte]: ...

    @abstractmethod
    def detalle(self, importacion_id: int) -> ImportacionSoporte | None: ...
