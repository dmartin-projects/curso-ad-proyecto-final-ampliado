# estadisticas/application/obtener_tendencia_use_case/i_obtener_tendencia_use_case.py (módulo 89)
from abc import ABC, abstractmethod

from estadisticas.application.obtener_tendencia_use_case.dtos.obtener_tendencia_input_dto import (
    ObtenerTendenciaInputDTO,
)
from estadisticas.application.obtener_tendencia_use_case.dtos.tendencia_output_dto import TendenciaOutputDTO


class IObtenerTendenciaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerTendenciaInputDTO) -> TendenciaOutputDTO: ...
