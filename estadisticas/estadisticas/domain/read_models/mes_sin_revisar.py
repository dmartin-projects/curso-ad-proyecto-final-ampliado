# estadisticas/domain/read_models/mes_sin_revisar.py — lo que queda por revisar en un mes (módulo 89)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MesSinRevisar:
    mes: str
    movimientos: int
    gastos: Decimal
