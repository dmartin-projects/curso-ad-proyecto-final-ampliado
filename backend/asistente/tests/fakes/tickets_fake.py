# asistente/tests/fakes/tickets_fake.py — ITickets en memoria (módulo 95)
from asistente.application.ports.i_tickets import ITickets
from asistente.domain.read_models.ticket_leido import TicketLeido
from core.domain.enums.rol import Rol


class TicketsFake(ITickets):
    def __init__(self, tickets: dict[tuple[int, int], TicketLeido] | None = None):
        self.tickets = dict(tickets or {})  # {(hogar_id, ticket_id): …}

    def ticket(self, actor, hogar_id, ticket_id):
        actor.exigir(Rol.LECTOR)
        return self.tickets.get((hogar_id, ticket_id))
