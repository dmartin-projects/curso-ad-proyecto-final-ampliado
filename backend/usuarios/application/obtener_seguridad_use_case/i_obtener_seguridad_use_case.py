# usuarios/application/obtener_seguridad_use_case/i_obtener_seguridad_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.obtener_seguridad_use_case.dtos.obtener_seguridad_input_dto import ObtenerSeguridadInputDTO
from usuarios.application.obtener_seguridad_use_case.dtos.seguridad_output_dto import SeguridadOutputDTO


class IObtenerSeguridadUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerSeguridadInputDTO) -> SeguridadOutputDTO: ...
