# backoffice/application/localizar_tickets_use_case/localizar_tickets_use_case.py (módulo 88)
from backoffice.application.localizar_tickets_use_case.dtos.localizar_tickets_input_dto import LocalizarTicketsInputDTO
from backoffice.application.localizar_tickets_use_case.i_localizar_tickets_use_case import ILocalizarTicketsUseCase
from backoffice.domain.repositories.i_ticket_soporte_query_service import ITicketSoporteQueryService


class LocalizarTicketsUseCase(ILocalizarTicketsUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, tickets: ITicketSoporteQueryService):
        self.tickets = tickets

    def ejecutar(self, entrada: LocalizarTicketsInputDTO) -> list[tuple[int, int]]:
        return self.tickets.localizar(list(entrada.ids))
