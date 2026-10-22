# finanzas/domain/events/movimientos_apuntados_event.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class MovimientosApuntadosEvent:
    """Los que trae un proceso (ticket, extracto), muchos de una vez."""

    hogar_id: int
    ids: tuple[int, ...]
    meses: frozenset[Mes]
