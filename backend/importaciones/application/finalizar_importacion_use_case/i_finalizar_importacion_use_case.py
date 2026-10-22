# importaciones/application/finalizar_importacion_use_case/i_finalizar_importacion_use_case.py (módulos 75 y 88)
from abc import ABC, abstractmethod

from importaciones.application.finalizar_importacion_use_case.dtos.finalizar_importacion_input_dto import (
    FinalizarImportacionInputDTO,
)
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO


class IFinalizarImportacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: FinalizarImportacionInputDTO) -> ImportacionOutputDTO: ...
