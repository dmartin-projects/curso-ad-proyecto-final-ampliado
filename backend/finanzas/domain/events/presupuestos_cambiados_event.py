# finanzas/domain/events/presupuestos_cambiados_event.py (módulos 85 y 87)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class PresupuestosCambiadosEvent:
    hogar_id: int
    meses: frozenset[Mes]
