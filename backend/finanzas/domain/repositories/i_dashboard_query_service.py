# finanzas/domain/repositories/i_dashboard_query_service.py — el lado de LECTURA del dashboard (CQRS, módulo 87)
from abc import ABC, abstractmethod

from finanzas.domain.read_models.dashboard import Dashboard
from finanzas.domain.repositories.queries.dashboard_query import DashboardQuery


class IDashboardQueryService(ABC):
    """Lee sin pasar por los BOs: agregaciones en la base de datos que devuelven un read model."""

    @abstractmethod
    def resumen(self, query: DashboardQuery) -> Dashboard:
        """Totales del mes y del anterior, gasto por categoría principal, acumulado diario, los últimos 12 meses,
        los comercios donde más se gasta, los presupuestos con lo gastado y los movimientos sin revisar."""
