# finanzas/domain/repositories/i_presupuesto_query_service.py (módulos 76 y 87)
from abc import ABC, abstractmethod

from finanzas.domain.read_models.presupuesto_con_gastado import PresupuestoConGastado
from finanzas.domain.repositories.queries.presupuestos_query import PresupuestosQuery


class IPresupuestoQueryService(ABC):
    @abstractmethod
    def listar(self, query: PresupuestosQuery) -> list[PresupuestoConGastado]:
        """Con lo gastado en su categoría y subcategorías, en una sola consulta (sin N+1)."""

    @abstractmethod
    def detalle(self, hogar_id: int, presupuesto_id: int) -> PresupuestoConGastado | None: ...
