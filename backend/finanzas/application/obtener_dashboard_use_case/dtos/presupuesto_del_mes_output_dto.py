# finanzas/application/obtener_dashboard_use_case/dtos/presupuesto_del_mes_output_dto.py (módulo 87)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PresupuestoDelMesOutputDTO:
    categoria: str
    importe: Decimal
    gastado: Decimal
    porcentaje: int
