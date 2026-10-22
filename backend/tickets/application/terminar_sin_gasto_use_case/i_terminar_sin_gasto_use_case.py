# tickets/application/terminar_sin_gasto_use_case/i_terminar_sin_gasto_use_case.py (módulos 74 y 88)
from abc import ABC, abstractmethod

from tickets.application.terminar_sin_gasto_use_case.dtos.terminar_sin_gasto_input_dto import TerminarSinGastoInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket


class ITerminarSinGastoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: TerminarSinGastoInputDTO) -> EstadoTicket | None: ...
