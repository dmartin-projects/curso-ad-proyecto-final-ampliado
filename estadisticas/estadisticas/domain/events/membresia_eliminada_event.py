# estadisticas/domain/events/membresia_eliminada_event.py — un tombstone del topic de membresías (módulo 89)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MembresiaEliminadaEvent:
    hogar_id: int
    usuario_id: int
    version: int
