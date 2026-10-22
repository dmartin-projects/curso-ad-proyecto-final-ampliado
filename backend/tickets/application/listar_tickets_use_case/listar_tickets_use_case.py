# tickets/application/listar_tickets_use_case/listar_tickets_use_case.py (módulo 88)
from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from core.domain.enums.rol import Rol
from tickets.application.listar_tickets_use_case.dtos.listar_tickets_input_dto import ListarTicketsInputDTO
from tickets.application.listar_tickets_use_case.i_listar_tickets_use_case import IListarTicketsUseCase
from tickets.application.shared.dtos.ticket_listado_output_dto import TicketListadoOutputDTO
from tickets.domain.repositories.i_ticket_query_service import ITicketQueryService
from tickets.domain.repositories.queries.tickets_query import TicketsQuery


class ListarTicketsUseCase(IListarTicketsUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, tickets: ITicketQueryService):
        self.tickets = tickets

    def ejecutar(self, entrada: ListarTicketsInputDTO) -> PaginaOutputDTO[TicketListadoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        query = TicketsQuery(
            entrada.hogar_id, entrada.estado, entrada.cuenta_id, entrada.busqueda, entrada.orden, entrada.paginacion
        )
        return PaginaOutputDTO.desde_pagina(self.tickets.listar(query), TicketListadoOutputDTO.desde_read_model)
