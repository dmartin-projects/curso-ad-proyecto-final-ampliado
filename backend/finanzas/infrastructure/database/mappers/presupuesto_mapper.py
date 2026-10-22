# finanzas/infrastructure/database/mappers/presupuesto_mapper.py — BO ↔ fila (módulo 87)
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.domain.bo.presupuesto import Presupuesto
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel


def presupuesto_a_bo(fila: PresupuestoModel) -> Presupuesto:
    return Presupuesto(
        id=fila.pk,
        hogar_id=fila.hogar_id,
        categoria_id=fila.categoria_id,
        mes=Mes.de(fila.mes),
        importe=Dinero(fila.importe),
        alerta_enviada=fila.alerta_enviada,
    )


def presupuesto_a_modelo(p: Presupuesto) -> PresupuestoModel:
    return PresupuestoModel(
        pk=p.id,
        hogar_id=p.hogar_id,
        categoria_id=p.categoria_id,
        mes=p.mes.inicio,
        importe=p.importe.cantidad,
        alerta_enviada=p.alerta_enviada,
    )
