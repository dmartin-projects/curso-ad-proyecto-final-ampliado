# tickets/application/terminar_sin_gasto_use_case/terminar_sin_gasto_use_case.py (módulos 74 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from tickets.application.terminar_sin_gasto_use_case.dtos.terminar_sin_gasto_input_dto import TerminarSinGastoInputDTO
from tickets.application.terminar_sin_gasto_use_case.i_terminar_sin_gasto_use_case import ITerminarSinGastoUseCase
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.events.ticket_terminado_event import TicketTerminadoEvent
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository


class TerminarSinGastoUseCase(ITerminarSinGastoUseCase):
    """`error` (se puede reprocesar) o `revisar` (la persona introduce los datos a mano). Lo pide el sistema: la
    tarea cuando se queda sin reintentos."""

    def __init__(
        self, *, tickets: ITicketCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo, reloj: IReloj
    ):
        self.tickets, self.eventos, self.uow, self.reloj = tickets, eventos, uow, reloj

    def ejecutar(self, entrada: TerminarSinGastoInputDTO) -> EstadoTicket | None:
        with self.uow:
            if not self.tickets.terminar_sin_gasto(
                entrada.ticket_id, entrada.estado, entrada.mensaje[:1000], self.reloj.ahora()
            ):
                return None  # ya estaba terminado
            self.eventos.publicar(TicketTerminadoEvent(entrada.ticket_id))
        return entrada.estado
