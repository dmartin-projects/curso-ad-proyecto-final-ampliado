# estadisticas/domain/read_models/mes_de_tendencia.py — un mes de la tendencia, tal como se lee (módulo 89)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MesDeTendencia:
    mes: str  # "2026-10"
    gastos: Decimal
    ingresos: Decimal
    ahorro: Decimal
