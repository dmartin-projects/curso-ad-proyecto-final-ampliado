# usuarios/application/cerrar_sesion_use_case/i_cerrar_sesion_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.cerrar_sesion_use_case.dtos.cerrar_sesion_input_dto import CerrarSesionInputDTO


class ICerrarSesionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CerrarSesionInputDTO) -> None: ...
