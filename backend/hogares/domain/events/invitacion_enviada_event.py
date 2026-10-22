# hogares/domain/events/invitacion_enviada_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class InvitacionEnviadaEvent:
    invitacion_id: int  # → el email, cuando se confirme
