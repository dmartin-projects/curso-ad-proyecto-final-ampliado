# asistente/domain/read_models/gasto_de_categoria.py (módulo 94)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class GastoDeCategoria:
    categoria: str  # la categoría principal (las subcategorías suman en ella), o "Sin categoría"
    total: Decimal
    porcentaje: Decimal  # del gasto del mes
