# importaciones/application/obtener_importacion_use_case/dtos/obtener_importacion_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerImportacionInputDTO:
    hogar_id: int
    actor: Actor
    importacion_id: int
