# asistente/application/ports/i_tickets.py — los tickets del hogar, vistos desde el asistente (módulo 95)
from abc import ABC, abstractmethod

from asistente.domain.read_models.ticket_leido import TicketLeido
from core.domain.vo.actor import Actor


class ITickets(ABC):
    @abstractmethod
    def ticket(self, actor: Actor, hogar_id: int, ticket_id: int) -> TicketLeido | None:
        """El ticket de ESE hogar, o None (exista en otro o no)."""
