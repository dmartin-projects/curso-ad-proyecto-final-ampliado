# backoffice/domain/repositories/i_movimiento_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.movimiento_soporte import MovimientoSoporte
from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery
from core.domain.read_models.pagina import Pagina


class IMovimientoSoporteQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoSoporteQuery) -> Pagina[MovimientoSoporte]: ...

    @abstractmethod
    def detalle(self, movimiento_id: int) -> MovimientoSoporte | None: ...

    @abstractmethod
    def hogar_de_categoria(self, categoria_id: int) -> int | None: ...
