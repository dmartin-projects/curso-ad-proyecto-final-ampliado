# backoffice/application/listar_tickets_soporte_use_case/i_listar_tickets_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.listar_tickets_soporte_use_case.dtos.listar_tickets_soporte_input_dto import (
    ListarTicketsSoporteInputDTO,
)
from backoffice.application.shared.dtos.ticket_soporte_output_dto import TicketSoporteOutputDTO
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class IListarTicketsSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarTicketsSoporteInputDTO) -> PaginaOutputDTO[TicketSoporteOutputDTO]: ...
