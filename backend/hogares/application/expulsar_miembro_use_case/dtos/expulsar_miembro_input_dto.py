# hogares/application/expulsar_miembro_use_case/dtos/expulsar_miembro_input_dto.py (módulos 71 y 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ExpulsarMiembroInputDTO:
    hogar_id: int
    actor: Actor
    membresia_id: int
