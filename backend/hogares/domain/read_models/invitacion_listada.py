# hogares/domain/read_models/invitacion_listada.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InvitacionListada:
    id: int
    email: str
    rol: str
    caduca: datetime
    aceptada: datetime | None
