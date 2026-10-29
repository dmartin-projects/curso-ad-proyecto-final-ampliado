# finanzas/domain/read_models/totales_de_movimientos.py — cuántos movimientos cumplen unos filtros y cuánto suman (módulo 95)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class TotalesDeMovimientos:
    num: int
    gastos: Decimal  # en positivo
    ingresos: Decimal
