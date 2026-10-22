# hogares/domain/events/miembro_anadido_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class MiembroAnadidoEvent:
    hogar_id: int
    usuario_id: int
    rol: str
