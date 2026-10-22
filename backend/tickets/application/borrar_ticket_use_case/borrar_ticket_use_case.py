# tickets/application/borrar_ticket_use_case/borrar_ticket_use_case.py (módulos 74 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from tickets.application.borrar_ticket_use_case.dtos.borrar_ticket_input_dto import BorrarTicketInputDTO
from tickets.application.borrar_ticket_use_case.i_borrar_ticket_use_case import IBorrarTicketUseCase
from tickets.domain.events.ticket_borrado_event import TicketBorradoEvent
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository


class BorrarTicketUseCase(IBorrarTicketUseCase):
    """El ticket y su archivo (cuando se confirma la transacción). El gasto, si lo hay, se queda."""

    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, tickets: ITicketCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.tickets, self.eventos, self.uow = tickets, eventos, uow

    def ejecutar(self, entrada: BorrarTicketInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            ticket = self.tickets.obtener(entrada.hogar_id, entrada.ticket_id)
            self.tickets.eliminar(ticket)
            self.eventos.publicar(TicketBorradoEvent(ticket.archivo))
