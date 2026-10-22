# estadisticas/application/obtener_sin_revisar_use_case/i_obtener_sin_revisar_use_case.py (módulo 89)
from abc import ABC, abstractmethod

from estadisticas.application.obtener_sin_revisar_use_case.dtos.obtener_sin_revisar_input_dto import (
    ObtenerSinRevisarInputDTO,
)
from estadisticas.application.obtener_sin_revisar_use_case.dtos.sin_revisar_output_dto import SinRevisarOutputDTO


class IObtenerSinRevisarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerSinRevisarInputDTO) -> SinRevisarOutputDTO: ...
