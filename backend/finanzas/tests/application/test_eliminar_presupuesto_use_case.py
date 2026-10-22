"""EliminarPresupuestoUseCase con los fakes (módulo 87)."""

from core.domain.enums.rol import Rol
from finanzas.application.eliminar_presupuesto_use_case.dtos.eliminar_presupuesto_input_dto import (
    EliminarPresupuestoInputDTO,
)
from finanzas.domain.events.presupuestos_cambiados_event import PresupuestosCambiadosEvent
from finanzas.tests.fakes.mundo import HOGAR, OCTUBRE, actor


def test_eliminar_presupuesto_avisa(mundo):
    p = mundo.presupuesto(mundo.categoria("Súper"))
    mundo.eliminar_presupuesto.ejecutar(EliminarPresupuestoInputDTO(HOGAR, actor(Rol.ADMIN), p.id))
    assert mundo.presupuestos.todos() == []
    assert mundo.eventos.publicados == [PresupuestosCambiadosEvent(HOGAR, frozenset({OCTUBRE}))]
