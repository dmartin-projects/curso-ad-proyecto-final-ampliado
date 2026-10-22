# usuarios/application/cambiar_contrasena_use_case/i_cambiar_contrasena_use_case.py (módulos 35 y 88)
from abc import ABC, abstractmethod

from usuarios.application.cambiar_contrasena_use_case.dtos.cambiar_contrasena_input_dto import CambiarContrasenaInputDTO


class ICambiarContrasenaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CambiarContrasenaInputDTO) -> None: ...
