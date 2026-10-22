# finanzas/domain/read_models/categoria_del_mes.py (módulos 77 y 87)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CategoriaDelMes:
    categoria: int | None  # la categoría PRINCIPAL (las subcategorías suman en su padre); None: sin categoría
    nombre: str
    color: str
    total: Decimal
    porcentaje: Decimal
