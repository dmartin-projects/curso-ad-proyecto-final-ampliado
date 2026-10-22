# finanzas/infrastructure/database/repositories/presupuesto_query_service_orm.py — IPresupuestoQueryService con el ORM
# (módulos 07, 76 y 87)
from finanzas.domain.read_models.presupuesto_con_gastado import PresupuestoConGastado
from finanzas.domain.repositories.i_presupuesto_query_service import IPresupuestoQueryService
from finanzas.domain.repositories.queries.presupuestos_query import PresupuestosQuery
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel


def _a_read_model(p: PresupuestoModel) -> PresupuestoConGastado:
    return PresupuestoConGastado(id=p.pk, categoria_id=p.categoria_id, mes=p.mes, importe=p.importe, gastado=p.gastado)


class PresupuestoQueryServiceORM(IPresupuestoQueryService):
    @staticmethod
    def _con_gastado(hogar_id: int):
        # Subquery correlacionada (módulos 07 y 76): lo gastado de todos los presupuestos en una consulta
        return PresupuestoModel.objects.filter(hogar_id=hogar_id).select_related("categoria").con_gastado()

    def listar(self, query: PresupuestosQuery) -> list[PresupuestoConGastado]:
        qs = self._con_gastado(query.hogar_id)
        if query.mes is not None:
            qs = qs.filter(mes=query.mes.inicio)
        return [_a_read_model(p) for p in qs.order_by(*(query.orden or ("categoria__orden",)))]

    def detalle(self, hogar_id: int, presupuesto_id: int) -> PresupuestoConGastado | None:
        fila = self._con_gastado(hogar_id).filter(pk=presupuesto_id).first()
        return None if fila is None else _a_read_model(fila)
