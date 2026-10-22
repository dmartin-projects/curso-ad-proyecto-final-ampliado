# backoffice/application/obtener_resumen_soporte_use_case/i_obtener_resumen_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_resumen_soporte_use_case.dtos.obtener_resumen_soporte_input_dto import (
    ObtenerResumenSoporteInputDTO,
)
from backoffice.application.shared.dtos.resumen_soporte_output_dto import ResumenSoporteOutputDTO


class IObtenerResumenSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerResumenSoporteInputDTO) -> ResumenSoporteOutputDTO: ...
