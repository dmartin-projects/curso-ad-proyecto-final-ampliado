# finanzas/domain/events/movimientos_recategorizados_event.py (módulos 85 y 87)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class MovimientosRecategorizadosEvent:
    hogar_id: int
    ids: tuple[int, ...]
    meses: frozenset[Mes]
