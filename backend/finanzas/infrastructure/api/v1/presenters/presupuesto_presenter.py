# finanzas/infrastructure/api/v1/presenters/presupuesto_presenter.py — del OutputDTO a lo que lee el serializer
# (módulo 87)
from types import SimpleNamespace

from finanzas.application.shared.dtos.presupuesto_con_gastado_output_dto import PresupuestoConGastadoOutputDTO


def presentar(p: PresupuestoConGastadoOutputDTO) -> SimpleNamespace:
    return SimpleNamespace(
        id=p.id,
        categoria=SimpleNamespace(pk=p.categoria_id),  # PrimaryKeyRelatedField lee .pk
        mes=p.mes,
        importe=p.importe,
        gastado=p.gastado,
    )
