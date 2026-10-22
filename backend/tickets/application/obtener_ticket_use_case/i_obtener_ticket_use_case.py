# tickets/application/obtener_ticket_use_case/i_obtener_ticket_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from tickets.application.obtener_ticket_use_case.dtos.obtener_ticket_input_dto import ObtenerTicketInputDTO
from tickets.application.shared.dtos.ticket_listado_output_dto import TicketListadoOutputDTO


class IObtenerTicketUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerTicketInputDTO) -> TicketListadoOutputDTO | None: ...
