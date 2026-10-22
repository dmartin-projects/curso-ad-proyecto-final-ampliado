# importaciones/application/finalizar_importacion_use_case/dtos/finalizar_importacion_input_dto.py (módulos 75 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class FinalizarImportacionInputDTO:
    importacion_id: int
