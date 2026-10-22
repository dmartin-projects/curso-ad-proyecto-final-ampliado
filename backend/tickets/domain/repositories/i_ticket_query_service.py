# tickets/domain/repositories/i_ticket_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from core.domain.read_models.pagina import Pagina
from tickets.domain.read_models.ticket_listado import TicketListado
from tickets.domain.repositories.queries.tickets_query import TicketsQuery


class ITicketQueryService(ABC):
    @abstractmethod
    def listar(self, query: TicketsQuery) -> Pagina[TicketListado]:
        """Los tickets del hogar con sus líneas y su gasto (sin N+1), los más recientes primero."""

    @abstractmethod
    def detalle(self, hogar_id: int, ticket_id: int) -> TicketListado | None: ...

    @abstractmethod
    def contar_atascados(self) -> int:
        """Pendientes o procesando sin moverse desde hace ATASCADO (soporte, módulo 79; métrica, módulo 84)."""
