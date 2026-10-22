# backoffice/application/obtener_ticket_soporte_use_case/obtener_ticket_soporte_use_case.py (módulo 88)
from backoffice.application.obtener_ticket_soporte_use_case.dtos.obtener_ticket_soporte_input_dto import (
    ObtenerTicketSoporteInputDTO,
)
from backoffice.application.obtener_ticket_soporte_use_case.i_obtener_ticket_soporte_use_case import (
    IObtenerTicketSoporteUseCase,
)
from backoffice.application.shared.dtos.ticket_soporte_output_dto import TicketSoporteOutputDTO
from backoffice.domain.repositories.i_ticket_soporte_query_service import ITicketSoporteQueryService


class ObtenerTicketSoporteUseCase(IObtenerTicketSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, tickets: ITicketSoporteQueryService):
        self.tickets = tickets

    def ejecutar(self, entrada: ObtenerTicketSoporteInputDTO) -> TicketSoporteOutputDTO | None:
        leido = self.tickets.detalle(entrada.ticket_id)
        return None if leido is None else TicketSoporteOutputDTO.desde_read_model(leido)
