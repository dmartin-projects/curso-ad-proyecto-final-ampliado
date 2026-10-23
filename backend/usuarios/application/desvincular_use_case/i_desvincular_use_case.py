# usuarios/application/desvincular_use_case/i_desvincular_use_case.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.desvincular_use_case.dtos.desvincular_input_dto import DesvincularInputDTO


class IDesvincularUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: DesvincularInputDTO) -> None: ...
