# importaciones/application/deshacer_importacion_use_case/i_deshacer_importacion_use_case.py (módulos 75 y 88)
from abc import ABC, abstractmethod

from importaciones.application.deshacer_importacion_use_case.dtos.deshacer_importacion_input_dto import (
    DeshacerImportacionInputDTO,
)
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO


class IDeshacerImportacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: DeshacerImportacionInputDTO) -> ImportacionOutputDTO: ...
