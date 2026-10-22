# finanzas/domain/read_models/presupuesto_con_gastado.py (módulos 76 y 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PresupuestoConGastado:
    id: int
    categoria_id: int
    mes: date  # día 1
    importe: Decimal
    gastado: Decimal  # negativo: son gastos
