# tickets/application/procesar_ticket_use_case/i_procesar_ticket_use_case.py (módulos 74 y 88)
from abc import ABC, abstractmethod

from tickets.application.procesar_ticket_use_case.dtos.procesar_ticket_input_dto import ProcesarTicketInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket


class IProcesarTicketUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ProcesarTicketInputDTO) -> EstadoTicket | None: ...
