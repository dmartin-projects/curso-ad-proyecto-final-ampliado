# backoffice/application/listar_tickets_soporte_use_case/listar_tickets_soporte_use_case.py (módulo 88)
from backoffice.application.listar_tickets_soporte_use_case.dtos.listar_tickets_soporte_input_dto import (
    ListarTicketsSoporteInputDTO,
)
from backoffice.application.listar_tickets_soporte_use_case.i_listar_tickets_soporte_use_case import (
    IListarTicketsSoporteUseCase,
)
from backoffice.application.shared.dtos.ticket_soporte_output_dto import TicketSoporteOutputDTO
from backoffice.domain.repositories.i_ticket_soporte_query_service import ITicketSoporteQueryService
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class ListarTicketsSoporteUseCase(IListarTicketsSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, tickets: ITicketSoporteQueryService):
        self.tickets = tickets

    def ejecutar(self, entrada: ListarTicketsSoporteInputDTO) -> PaginaOutputDTO[TicketSoporteOutputDTO]:
        pagina = self.tickets.listar(entrada.query, solo_atascados=entrada.solo_atascados)
        return PaginaOutputDTO.desde_pagina(pagina, TicketSoporteOutputDTO.desde_read_model)
