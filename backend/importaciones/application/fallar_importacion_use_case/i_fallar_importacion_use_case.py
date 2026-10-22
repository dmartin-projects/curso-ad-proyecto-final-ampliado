# importaciones/application/fallar_importacion_use_case/i_fallar_importacion_use_case.py (módulos 75 y 88)
from abc import ABC, abstractmethod

from importaciones.application.fallar_importacion_use_case.dtos.fallar_importacion_input_dto import (
    FallarImportacionInputDTO,
)


class IFallarImportacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: FallarImportacionInputDTO) -> None: ...
