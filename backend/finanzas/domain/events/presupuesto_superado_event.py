# finanzas/domain/events/presupuesto_superado_event.py (módulos 85 y 87)
from dataclasses import dataclass

from core.domain.vo.dinero import Dinero


@dataclass(frozen=True)
class PresupuestoSuperadoEvent:
    presupuesto_id: int
    gastado: Dinero
