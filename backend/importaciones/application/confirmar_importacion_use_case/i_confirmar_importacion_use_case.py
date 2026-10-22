# importaciones/application/confirmar_importacion_use_case/i_confirmar_importacion_use_case.py (módulos 75 y 88)
from abc import ABC, abstractmethod

from importaciones.application.confirmar_importacion_use_case.dtos.confirmar_importacion_input_dto import (
    ConfirmarImportacionInputDTO,
)
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO


class IConfirmarImportacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ConfirmarImportacionInputDTO) -> ImportacionOutputDTO: ...
