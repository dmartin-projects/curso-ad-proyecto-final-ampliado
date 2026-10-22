"""RecategorizarMovimientosUseCase con los fakes (módulos 87 y 88)."""

from datetime import date

import pytest

from core.domain.enums.accion import Accion
from core.domain.vo.mes import Mes
from finanzas.application.recategorizar_movimientos_use_case.dtos.recategorizar_movimientos_input_dto import (
    RecategorizarMovimientosInputDTO,
)
from finanzas.domain.events.movimientos_recategorizados_event import MovimientosRecategorizadosEvent
from finanzas.domain.exceptions.categoria_no_encontrada_exception import CategoriaNoEncontradaException
from finanzas.tests.fakes.mundo import HOGAR, OTRO_HOGAR, actor


def test_recategorizar_solo_los_del_hogar_y_los_marca_revisados(mundo):
    super_ = mundo.categoria("Súper")
    mios = [mundo.movimiento(revisado=False, fecha=date(2026, 9, 10)) for _ in range(3)]
    ajeno = mundo.movimiento(hogar_id=OTRO_HOGAR)

    n = mundo.recategorizar.ejecutar(
        RecategorizarMovimientosInputDTO(HOGAR, actor(), tuple(m.id for m in mios) + (ajeno.id,), super_.id)
    )

    assert n == 3
    assert {(m.categoria_id, m.revisado) for m in mundo.movimientos.todos() if m.hogar_id == HOGAR} == {
        (super_.id, True)
    }
    assert mundo.movimientos.obtener(OTRO_HOGAR, ajeno.id).categoria_id is None
    assert mundo.eventos.publicados == [
        MovimientosRecategorizadosEvent(HOGAR, tuple(m.id for m in mios), frozenset({Mes(2026, 9)}))
    ]


def test_recategorizar_con_una_categoria_de_otro_hogar(mundo):
    ajena = mundo.categoria("Ajena", hogar_id=OTRO_HOGAR)
    m = mundo.movimiento()
    with pytest.raises(CategoriaNoEncontradaException) as e:
        mundo.recategorizar.ejecutar(RecategorizarMovimientosInputDTO(HOGAR, actor(), (m.id,), ajena.id))
    assert e.value.campo == "categoria"


def test_recategorizar_audita_cada_movimiento(mundo):
    super_ = mundo.categoria("Súper")
    mios = [mundo.movimiento(revisado=False) for _ in range(2)]

    mundo.recategorizar.ejecutar(RecategorizarMovimientosInputDTO(HOGAR, actor(), tuple(m.id for m in mios), super_.id))

    assert [(r[0], r[2], r[4]) for r in mundo.auditoria.registros] == [
        (Accion.MODIFICAR, m.id, {"categoria": ["None", str(super_.id)], "revisado": ["False", "True"]}) for m in mios
    ]


def test_recategorizar_tambien_audita(mundo):  # lo pida la API o el backoffice
    super_ = mundo.categoria("Súper")
    m = mundo.movimiento(revisado=False)
    mundo.recategorizar.ejecutar(RecategorizarMovimientosInputDTO(HOGAR, actor(), (m.id,), super_.id))
    assert mundo.auditoria.registros == [
        (
            Accion.MODIFICAR,
            "finanzas.movimiento",
            m.id,
            7,
            {"categoria": ["None", str(super_.id)], "revisado": ["False", "True"]},
        )
    ]
