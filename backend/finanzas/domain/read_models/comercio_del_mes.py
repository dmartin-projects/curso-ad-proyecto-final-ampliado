# finanzas/domain/read_models/comercio_del_mes.py (módulos 77 y 87)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ComercioDelMes:
    comercio: int
    nombre: str
    total: Decimal
    veces: int
