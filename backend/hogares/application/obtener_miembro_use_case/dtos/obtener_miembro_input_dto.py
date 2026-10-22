# hogares/application/obtener_miembro_use_case/dtos/obtener_miembro_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerMiembroInputDTO:
    hogar_id: int
    actor: Actor
    membresia_id: int
