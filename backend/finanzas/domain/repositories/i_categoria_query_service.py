# finanzas/domain/repositories/i_categoria_query_service.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.domain.read_models.categoria_listada import CategoriaListada
from finanzas.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery


class ICategoriaQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoDelHogarQuery) -> list[CategoriaListada]: ...

    @abstractmethod
    def detalle(self, hogar_id: int, categoria_id: int) -> CategoriaListada | None: ...
