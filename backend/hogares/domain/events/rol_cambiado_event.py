# hogares/domain/events/rol_cambiado_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class RolCambiadoEvent:
    hogar_id: int
    usuario_id: int
    rol: str
