# finanzas/application/obtener_dashboard_use_case/dtos/obtener_dashboard_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class ObtenerDashboardInputDTO:
    hogar_id: int
    actor: Actor
    mes: Mes
