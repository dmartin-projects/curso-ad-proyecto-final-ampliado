# asistente/domain/read_models/gasto_de_comercio.py (módulo 95)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class GastoDeComercio:
    comercio: str
    total: Decimal
    veces: int
