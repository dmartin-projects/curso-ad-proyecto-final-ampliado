# usuarios/application/establecer_contrasena_use_case/i_establecer_contrasena_use_case.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.establecer_contrasena_use_case.dtos.establecer_contrasena_input_dto import (
    EstablecerContrasenaInputDTO,
)


class IEstablecerContrasenaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EstablecerContrasenaInputDTO) -> None: ...
