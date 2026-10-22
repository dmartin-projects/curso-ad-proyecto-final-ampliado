# finanzas/domain/events/movimiento_modificado_event.py (módulos 85 y 87)
from dataclasses import dataclass

from core.domain.vo.mes import Mes
from finanzas.domain.bo.movimiento import Movimiento


@dataclass(frozen=True)
class MovimientoModificadoEvent:
    movimiento: Movimiento
    meses: frozenset[Mes]  # el de antes y el de después, si ha cambiado la fecha
