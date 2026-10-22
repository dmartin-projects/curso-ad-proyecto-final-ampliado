# finanzas/domain/events/movimientos_eliminados_event.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class MovimientosEliminadosEvent:
    """Varios de una vez: deshacer una importación, descartar el gasto que propuso un ticket."""

    hogar_id: int
    ids: tuple[int, ...]
    meses: frozenset[Mes]
