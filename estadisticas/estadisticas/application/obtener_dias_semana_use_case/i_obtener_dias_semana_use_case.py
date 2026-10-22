# estadisticas/application/obtener_dias_semana_use_case/i_obtener_dias_semana_use_case.py (módulo 89)
from abc import ABC, abstractmethod

from estadisticas.application.obtener_dias_semana_use_case.dtos.dias_semana_output_dto import DiasSemanaOutputDTO
from estadisticas.application.obtener_dias_semana_use_case.dtos.obtener_dias_semana_input_dto import (
    ObtenerDiasSemanaInputDTO,
)


class IObtenerDiasSemanaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerDiasSemanaInputDTO) -> DiasSemanaOutputDTO: ...
