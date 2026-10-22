# tickets/application/contar_tickets_atascados_use_case/contar_tickets_atascados_use_case.py (módulo 88)
from tickets.application.contar_tickets_atascados_use_case.dtos.contar_tickets_atascados_input_dto import (
    ContarTicketsAtascadosInputDTO,
)
from tickets.application.contar_tickets_atascados_use_case.i_contar_tickets_atascados_use_case import (
    IContarTicketsAtascadosUseCase,
)
from tickets.domain.repositories.i_ticket_query_service import ITicketQueryService


class ContarTicketsAtascadosUseCase(IContarTicketsAtascadosUseCase):
    """Lo piden la métrica (módulo 84) y la pantalla de soporte (módulo 79), sin persona: no exige rol."""

    def __init__(self, *, tickets: ITicketQueryService):
        self.tickets = tickets

    def ejecutar(self, entrada: ContarTicketsAtascadosInputDTO) -> int:
        return self.tickets.contar_atascados()
