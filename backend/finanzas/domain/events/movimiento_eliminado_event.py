# finanzas/domain/events/movimiento_eliminado_event.py (módulos 85 y 87)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class MovimientoEliminadoEvent:
    movimiento_id: int
    hogar_id: int
    mes: Mes
