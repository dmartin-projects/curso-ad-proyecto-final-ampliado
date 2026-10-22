# finanzas/domain/events/movimiento_registrado_event.py (módulos 85 y 87)
from dataclasses import dataclass

from finanzas.domain.bo.movimiento import Movimiento


@dataclass(frozen=True)
class MovimientoRegistradoEvent:
    movimiento: Movimiento  # una instantánea: el evento no cambia aunque el BO sí
