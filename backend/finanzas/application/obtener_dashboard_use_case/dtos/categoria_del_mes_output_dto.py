# finanzas/application/obtener_dashboard_use_case/dtos/categoria_del_mes_output_dto.py (módulo 87)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CategoriaDelMesOutputDTO:
    categoria: int | None
    nombre: str
    color: str
    total: Decimal
    porcentaje: Decimal
