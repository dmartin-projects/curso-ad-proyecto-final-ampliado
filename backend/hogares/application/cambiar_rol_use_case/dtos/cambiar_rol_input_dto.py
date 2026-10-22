# hogares/application/cambiar_rol_use_case/dtos/cambiar_rol_input_dto.py (módulos 71 y 88)
from dataclasses import dataclass

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class CambiarRolInputDTO:
    hogar_id: int
    actor: Actor
    membresia_id: int
    rol: Rol
