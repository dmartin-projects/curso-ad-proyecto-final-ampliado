# backoffice/application/obtener_importacion_soporte_use_case/i_obtener_importacion_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_importacion_soporte_use_case.dtos.obtener_importacion_soporte_input_dto import (
    ObtenerImportacionSoporteInputDTO,
)
from backoffice.application.shared.dtos.importacion_soporte_output_dto import ImportacionSoporteOutputDTO


class IObtenerImportacionSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerImportacionSoporteInputDTO) -> ImportacionSoporteOutputDTO | None: ...
