# importaciones/application/obtener_importacion_use_case/i_obtener_importacion_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from importaciones.application.obtener_importacion_use_case.dtos.obtener_importacion_input_dto import (
    ObtenerImportacionInputDTO,
)
from importaciones.application.shared.dtos.importacion_listada_output_dto import ImportacionListadaOutputDTO


class IObtenerImportacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerImportacionInputDTO) -> ImportacionListadaOutputDTO | None: ...
