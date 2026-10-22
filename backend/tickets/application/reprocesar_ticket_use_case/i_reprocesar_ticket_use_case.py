# tickets/application/reprocesar_ticket_use_case/i_reprocesar_ticket_use_case.py (módulos 74 y 88)
from abc import ABC, abstractmethod

from tickets.application.reprocesar_ticket_use_case.dtos.reprocesar_ticket_input_dto import ReprocesarTicketInputDTO
from tickets.application.shared.dtos.ticket_output_dto import TicketOutputDTO


class IReprocesarTicketUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ReprocesarTicketInputDTO) -> TicketOutputDTO: ...
