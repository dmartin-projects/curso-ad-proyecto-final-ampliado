"""ConciliarMovimientosUseCase y DesconciliarMovimientosUseCase con los fakes (módulo 88)."""

from finanzas.application.conciliar_movimientos_use_case.dtos.conciliar_movimientos_input_dto import (
    ConciliarMovimientosInputDTO,
)
from finanzas.application.desconciliar_movimientos_use_case.dtos.desconciliar_movimientos_input_dto import (
    DesconciliarMovimientosInputDTO,
)
from finanzas.tests.fakes.mundo import HOGAR, OTRO_HOGAR, actor


def test_conciliar_solo_los_libres_y_desconciliar(mundo):
    a, b = mundo.movimiento(), mundo.movimiento()
    ajeno = mundo.movimiento(hogar_id=OTRO_HOGAR)
    mundo.conciliar.ejecutar(ConciliarMovimientosInputDTO(HOGAR, actor(), {a.id: "h1"}))

    hechos = mundo.conciliar.ejecutar(
        ConciliarMovimientosInputDTO(HOGAR, actor(), {a.id: "h2", b.id: "h3", ajeno.id: "h4"})
    )

    assert hechos == [b.id]  # a ya tenía su fila del banco; el ajeno no existe para este hogar
    assert mundo.movimientos.obtener(HOGAR, a.id).huella == "h1"
    assert mundo.desconciliar.ejecutar(DesconciliarMovimientosInputDTO(HOGAR, actor(), (a.id, b.id))) == 2
    assert {m.huella for m in mundo.movimientos.obtener_varios(HOGAR, [a.id, b.id])} == {""}
    assert mundo.eventos.publicados == []  # la huella no cambia ningún número ni viaja a Kafka
