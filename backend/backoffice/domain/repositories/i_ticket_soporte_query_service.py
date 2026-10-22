# backoffice/domain/repositories/i_ticket_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.ticket_soporte import TicketSoporte
from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery
from core.domain.read_models.pagina import Pagina


class ITicketSoporteQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoSoporteQuery, *, solo_atascados: bool = False) -> Pagina[TicketSoporte]: ...

    @abstractmethod
    def detalle(self, ticket_id: int) -> TicketSoporte | None: ...

    @abstractmethod
    def localizar(self, ids: list[int]) -> list[tuple[int, int]]:
        """(ticket, hogar) de los que existen: los use cases de tickets trabajan dentro de un hogar."""
