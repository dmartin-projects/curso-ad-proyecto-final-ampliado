# tickets/application/listar_tickets_use_case/i_listar_tickets_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from tickets.application.listar_tickets_use_case.dtos.listar_tickets_input_dto import ListarTicketsInputDTO
from tickets.application.shared.dtos.ticket_listado_output_dto import TicketListadoOutputDTO


class IListarTicketsUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarTicketsInputDTO) -> PaginaOutputDTO[TicketListadoOutputDTO]: ...
