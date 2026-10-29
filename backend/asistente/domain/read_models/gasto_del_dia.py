# asistente/domain/read_models/gasto_del_dia.py (módulo 95)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class GastoDelDia:
    fecha: date
    gasto: Decimal
    acumulado: Decimal  # desde el día 1 del mes
