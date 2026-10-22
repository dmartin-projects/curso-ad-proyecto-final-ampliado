# finanzas/domain/repositories/queries/dashboard_query.py — qué dashboard se pide (módulo 87)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True, slots=True)
class DashboardQuery:
    hogar_id: int
    mes: Mes
