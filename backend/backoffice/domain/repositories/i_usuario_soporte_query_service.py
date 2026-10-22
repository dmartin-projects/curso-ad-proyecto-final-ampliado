# backoffice/domain/repositories/i_usuario_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.usuario_soporte import UsuarioSoporte
from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery
from core.domain.read_models.pagina import Pagina


class IUsuarioSoporteQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoSoporteQuery) -> Pagina[UsuarioSoporte]: ...

    @abstractmethod
    def detalle(self, usuario_id: int) -> UsuarioSoporte | None: ...
