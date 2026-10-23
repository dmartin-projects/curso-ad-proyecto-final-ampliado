# usuarios/application/obtener_factores_use_case/i_obtener_factores_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.obtener_factores_use_case.dtos.factores_disponibles_output_dto import (
    FactoresDisponiblesOutputDTO,
)
from usuarios.application.obtener_factores_use_case.dtos.obtener_factores_input_dto import ObtenerFactoresInputDTO


class IObtenerFactoresUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerFactoresInputDTO) -> FactoresDisponiblesOutputDTO: ...
