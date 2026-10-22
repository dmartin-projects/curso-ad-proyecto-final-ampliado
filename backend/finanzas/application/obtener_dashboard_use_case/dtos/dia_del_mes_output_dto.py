# finanzas/application/obtener_dashboard_use_case/dtos/dia_del_mes_output_dto.py (módulo 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DiaDelMesOutputDTO:
    fecha: date
    gasto: Decimal
    acumulado: Decimal
