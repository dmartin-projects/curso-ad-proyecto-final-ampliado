# finanzas/domain/read_models/presupuesto_del_mes.py (módulos 77 y 87)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PresupuestoDelMes:
    categoria: str
    importe: Decimal
    gastado: Decimal
    porcentaje: int
