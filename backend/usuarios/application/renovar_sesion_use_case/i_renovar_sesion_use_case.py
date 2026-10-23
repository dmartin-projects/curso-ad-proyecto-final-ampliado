# usuarios/application/renovar_sesion_use_case/i_renovar_sesion_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.renovar_sesion_use_case.dtos.renovar_sesion_input_dto import RenovarSesionInputDTO


class IRenovarSesionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: RenovarSesionInputDTO) -> bool: ...
