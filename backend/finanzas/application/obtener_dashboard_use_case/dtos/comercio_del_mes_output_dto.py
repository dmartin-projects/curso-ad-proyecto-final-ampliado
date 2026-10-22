# finanzas/application/obtener_dashboard_use_case/dtos/comercio_del_mes_output_dto.py (módulo 87)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ComercioDelMesOutputDTO:
    comercio: int
    nombre: str
    total: Decimal
    veces: int
