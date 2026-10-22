# estadisticas/domain/events/movimiento_guardado_event.py — Gastos ha creado o cambiado un movimiento (módulo 89)
from dataclasses import dataclass

from estadisticas.domain.bo.movimiento import Movimiento


@dataclass(frozen=True, slots=True)
class MovimientoGuardadoEvent:
    movimiento: Movimiento
