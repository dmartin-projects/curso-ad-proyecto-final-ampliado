# hogares/application/invitar_use_case/dtos/invitar_input_dto.py (módulos 71 y 88)
from dataclasses import dataclass

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class InvitarInputDTO:
    hogar_id: int
    actor: Actor
    email: str
    rol: Rol = Rol.MIEMBRO
