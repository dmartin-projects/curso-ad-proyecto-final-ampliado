# finanzas/application/obtener_dashboard_use_case/dtos/mes_en_resumen_output_dto.py (módulo 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MesEnResumenOutputDTO:
    mes: date
    gastos: Decimal
    ingresos: Decimal
