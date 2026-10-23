# usuarios/application/obtener_acceso_use_case/i_obtener_acceso_use_case.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.obtener_acceso_use_case.dtos.acceso_output_dto import AccesoOutputDTO
from usuarios.application.obtener_acceso_use_case.dtos.obtener_acceso_input_dto import ObtenerAccesoInputDTO


class IObtenerAccesoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerAccesoInputDTO) -> AccesoOutputDTO: ...
