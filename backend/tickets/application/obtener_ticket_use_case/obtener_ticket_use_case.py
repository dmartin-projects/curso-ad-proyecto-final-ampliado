# tickets/application/obtener_ticket_use_case/obtener_ticket_use_case.py (módulo 88)
from core.domain.enums.rol import Rol
from tickets.application.obtener_ticket_use_case.dtos.obtener_ticket_input_dto import ObtenerTicketInputDTO
from tickets.application.obtener_ticket_use_case.i_obtener_ticket_use_case import IObtenerTicketUseCase
from tickets.application.shared.dtos.ticket_listado_output_dto import TicketListadoOutputDTO
from tickets.domain.repositories.i_ticket_query_service import ITicketQueryService


class ObtenerTicketUseCase(IObtenerTicketUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, tickets: ITicketQueryService):
        self.tickets = tickets

    def ejecutar(self, entrada: ObtenerTicketInputDTO) -> TicketListadoOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leido = self.tickets.detalle(entrada.hogar_id, entrada.ticket_id)
        return None if leido is None else TicketListadoOutputDTO.desde_read_model(leido)
