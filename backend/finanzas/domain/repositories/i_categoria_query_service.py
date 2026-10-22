# finanzas/domain/repositories/i_categoria_query_service.py (módulo 87)
from abc import ABC, abstractmethod

from core.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from finanzas.domain.read_models.categoria_listada import CategoriaListada


class ICategoriaQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoDelHogarQuery) -> list[CategoriaListada]: ...

    @abstractmethod
    def detalle(self, hogar_id: int, categoria_id: int) -> CategoriaListada | None: ...
