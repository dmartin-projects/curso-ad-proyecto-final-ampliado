# usuarios/application/confirmar_recuperacion_use_case/i_confirmar_recuperacion_use_case.py (módulos 35 y 88)
from abc import ABC, abstractmethod

from usuarios.application.confirmar_recuperacion_use_case.dtos.confirmar_recuperacion_input_dto import (
    ConfirmarRecuperacionInputDTO,
)


class IConfirmarRecuperacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ConfirmarRecuperacionInputDTO) -> None: ...
