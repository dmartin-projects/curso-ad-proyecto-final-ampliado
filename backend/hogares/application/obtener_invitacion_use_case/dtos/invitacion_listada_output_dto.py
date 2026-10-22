# hogares/application/obtener_invitacion_use_case/dtos/invitacion_listada_output_dto.py (módulo 88)
from dataclasses import asdict, dataclass
from datetime import datetime

from hogares.domain.read_models.invitacion_listada import InvitacionListada


@dataclass(frozen=True, slots=True)
class InvitacionListadaOutputDTO:
    id: int
    email: str
    rol: str
    caduca: datetime
    aceptada: datetime | None

    @classmethod
    def desde_read_model(cls, rm: InvitacionListada) -> "InvitacionListadaOutputDTO":
        return cls(**asdict(rm))
