# importaciones/application/deshacer_importacion_use_case/dtos/deshacer_importacion_input_dto.py (módulos 75 y 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class DeshacerImportacionInputDTO:
    hogar_id: int
    actor: Actor
    importacion_id: int
