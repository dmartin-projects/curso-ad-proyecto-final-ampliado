# hogares/application/invitar_use_case/dtos/invitacion_output_dto.py (módulos 71 y 88)
from dataclasses import dataclass
from datetime import datetime

from hogares.domain.bo.invitacion import Invitacion


@dataclass(frozen=True, slots=True)
class InvitacionOutputDTO:
    id: int
    hogar_id: int
    email: str
    rol: str
    token: str
    caduca: datetime

    @classmethod
    def desde_bo(cls, i: Invitacion) -> "InvitacionOutputDTO":
        return cls(id=i.id, hogar_id=i.hogar_id, email=i.email, rol=str(i.rol), token=i.token, caduca=i.caduca)
