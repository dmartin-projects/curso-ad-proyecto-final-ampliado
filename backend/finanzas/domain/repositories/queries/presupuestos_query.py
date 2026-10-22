# finanzas/domain/repositories/queries/presupuestos_query.py (módulos 76 y 87)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True, slots=True)
class PresupuestosQuery:
    hogar_id: int
    mes: Mes | None = None  # None: todos los meses
    orden: tuple[str, ...] = ()  # vacío: por el orden de su categoría
