# tickets/application/confirmar_ticket_use_case/i_confirmar_ticket_use_case.py (módulos 74 y 88)
from abc import ABC, abstractmethod

from tickets.application.confirmar_ticket_use_case.dtos.confirmar_ticket_input_dto import ConfirmarTicketInputDTO
from tickets.application.shared.dtos.ticket_output_dto import TicketOutputDTO


class IConfirmarTicketUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ConfirmarTicketInputDTO) -> TicketOutputDTO: ...
