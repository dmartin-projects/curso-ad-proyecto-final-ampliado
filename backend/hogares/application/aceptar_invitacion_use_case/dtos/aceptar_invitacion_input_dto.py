# hogares/application/aceptar_invitacion_use_case/dtos/aceptar_invitacion_input_dto.py (módulos 71 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class AceptarInvitacionInputDTO:
    token: str
    usuario_id: int
    email: str  # el de la cuenta de quien acepta: tiene que ser el invitado
