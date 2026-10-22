# importaciones/domain/repositories/i_importacion_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from core.domain.read_models.pagina import Pagina
from importaciones.domain.read_models.fila_listada import FilaListada
from importaciones.domain.read_models.importacion_listada import ImportacionListada
from importaciones.domain.repositories.queries.filas_query import FilasQuery
from importaciones.domain.repositories.queries.importaciones_query import ImportacionesQuery


class IImportacionQueryService(ABC):
    @abstractmethod
    def listar(self, query: ImportacionesQuery) -> Pagina[ImportacionListada]: ...

    @abstractmethod
    def detalle(self, hogar_id: int, importacion_id: int) -> ImportacionListada | None: ...

    @abstractmethod
    def filas(self, query: FilasQuery) -> Pagina[FilaListada]:
        """La vista previa: cada fila con lo que se hará con ella, por número de línea."""
