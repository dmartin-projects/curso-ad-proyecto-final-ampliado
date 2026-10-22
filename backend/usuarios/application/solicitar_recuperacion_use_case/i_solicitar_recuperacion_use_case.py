# usuarios/application/solicitar_recuperacion_use_case/i_solicitar_recuperacion_use_case.py (módulos 35 y 88)
from abc import ABC, abstractmethod

from usuarios.application.solicitar_recuperacion_use_case.dtos.solicitar_recuperacion_input_dto import (
    SolicitarRecuperacionInputDTO,
)


class ISolicitarRecuperacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: SolicitarRecuperacionInputDTO) -> None: ...
