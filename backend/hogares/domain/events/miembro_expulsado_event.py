# hogares/domain/events/miembro_expulsado_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class MiembroExpulsadoEvent:
    hogar_id: int
    usuario_id: int
