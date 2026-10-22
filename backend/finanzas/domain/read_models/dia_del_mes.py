# finanzas/domain/read_models/dia_del_mes.py (módulos 77 y 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DiaDelMes:
    fecha: date
    gasto: Decimal
    acumulado: Decimal
