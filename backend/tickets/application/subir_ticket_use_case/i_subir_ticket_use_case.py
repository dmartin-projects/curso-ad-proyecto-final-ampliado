# tickets/application/subir_ticket_use_case/i_subir_ticket_use_case.py (módulos 74 y 88)
from abc import ABC, abstractmethod

from tickets.application.shared.dtos.ticket_output_dto import TicketOutputDTO
from tickets.application.subir_ticket_use_case.dtos.subir_ticket_input_dto import SubirTicketInputDTO


class ISubirTicketUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: SubirTicketInputDTO) -> TicketOutputDTO: ...
