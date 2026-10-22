# importaciones/application/fallar_importacion_use_case/dtos/fallar_importacion_input_dto.py (módulos 75 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class FallarImportacionInputDTO:
    importacion_id: int
    mensaje: str
