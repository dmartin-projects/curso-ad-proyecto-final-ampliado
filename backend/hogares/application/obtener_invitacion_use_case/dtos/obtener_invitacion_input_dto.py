# hogares/application/obtener_invitacion_use_case/dtos/obtener_invitacion_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerInvitacionInputDTO:
    hogar_id: int
    actor: Actor
    invitacion_id: int
