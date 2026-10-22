# tickets/application/borrar_ticket_use_case/i_borrar_ticket_use_case.py (módulos 74 y 88)
from abc import ABC, abstractmethod

from tickets.application.borrar_ticket_use_case.dtos.borrar_ticket_input_dto import BorrarTicketInputDTO


class IBorrarTicketUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: BorrarTicketInputDTO) -> None: ...
