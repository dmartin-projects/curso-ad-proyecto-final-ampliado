"""ComprobarPresupuestosUseCase con los fakes (módulos 76 y 87)."""

from core.domain.vo.dinero import Dinero
from finanzas.application.comprobar_presupuestos_use_case.dtos.comprobar_presupuestos_input_dto import (
    ComprobarPresupuestosInputDTO,
)
from finanzas.domain.events.presupuesto_superado_event import PresupuestoSuperadoEvent
from finanzas.tests.fakes.mundo import HOGAR, OCTUBRE

OCTUBRE_DEL_HOGAR = ComprobarPresupuestosInputDTO(HOGAR, (OCTUBRE,))


def test_comprobar_avisa_una_vez_cuenta_subcategorias_y_se_rearma(mundo):
    super_ = mundo.categoria("Súper")
    fruta = mundo.categoria("Fruta", padre=super_)
    p = mundo.presupuesto(super_, importe="100")
    mundo.movimiento(importe="-70", categoria=super_)
    assert mundo.comprobar.ejecutar(OCTUBRE_DEL_HOGAR) == []

    mundo.movimiento(importe="-40", categoria=fruta)  # la subcategoría cuenta
    [superado] = mundo.comprobar.ejecutar(OCTUBRE_DEL_HOGAR)
    assert superado.id == p.id
    assert mundo.eventos.publicados == [PresupuestoSuperadoEvent(p.id, Dinero("-110"))]
    assert mundo.comprobar.ejecutar(OCTUBRE_DEL_HOGAR) == []  # ya avisado

    for m in mundo.movimientos.todos():
        mundo.movimientos.eliminar(m)
    mundo.comprobar.ejecutar(OCTUBRE_DEL_HOGAR)
    assert mundo.presupuestos.obtener(HOGAR, p.id).alerta_enviada is False  # rearmado


def test_si_otro_proceso_se_adelanta_solo_avisa_el(mundo):
    super_ = mundo.categoria("Súper")
    mundo.presupuesto(super_, importe="10")
    mundo.movimiento(importe="-50", categoria=super_)
    mundo.presupuestos.carrera_perdida = True  # el UPDATE condicional no encuentra la fila "sin avisar"
    assert mundo.comprobar.ejecutar(OCTUBRE_DEL_HOGAR) == [] and mundo.eventos.publicados == []
