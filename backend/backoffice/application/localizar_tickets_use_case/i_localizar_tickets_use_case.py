# backoffice/application/localizar_tickets_use_case/i_localizar_tickets_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.localizar_tickets_use_case.dtos.localizar_tickets_input_dto import LocalizarTicketsInputDTO


class ILocalizarTicketsUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: LocalizarTicketsInputDTO) -> list[tuple[int, int]]: ...
