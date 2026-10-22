# tickets/application/contar_tickets_atascados_use_case/i_contar_tickets_atascados_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from tickets.application.contar_tickets_atascados_use_case.dtos.contar_tickets_atascados_input_dto import (
    ContarTicketsAtascadosInputDTO,
)


class IContarTicketsAtascadosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ContarTicketsAtascadosInputDTO) -> int: ...
