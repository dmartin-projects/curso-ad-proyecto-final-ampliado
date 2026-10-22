# estadisticas/domain/events/movimiento_eliminado_event.py — un tombstone del topic de movimientos (módulo 89)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MovimientoEliminadoEvent:
    id: int
    version: int
