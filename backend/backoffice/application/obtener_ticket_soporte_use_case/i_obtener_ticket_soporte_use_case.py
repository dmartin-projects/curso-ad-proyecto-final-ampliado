# backoffice/application/obtener_ticket_soporte_use_case/i_obtener_ticket_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_ticket_soporte_use_case.dtos.obtener_ticket_soporte_input_dto import (
    ObtenerTicketSoporteInputDTO,
)
from backoffice.application.shared.dtos.ticket_soporte_output_dto import TicketSoporteOutputDTO


class IObtenerTicketSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerTicketSoporteInputDTO) -> TicketSoporteOutputDTO | None: ...
