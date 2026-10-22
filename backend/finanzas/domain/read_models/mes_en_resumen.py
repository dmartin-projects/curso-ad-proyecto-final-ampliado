# finanzas/domain/read_models/mes_en_resumen.py (módulos 77 y 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MesEnResumen:
    mes: date
    gastos: Decimal
    ingresos: Decimal
