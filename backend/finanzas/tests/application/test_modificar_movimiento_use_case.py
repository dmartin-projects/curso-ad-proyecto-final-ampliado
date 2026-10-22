"""ModificarMovimientoUseCase con los fakes (módulo 87)."""

from datetime import date
from decimal import Decimal

import pytest

from core.domain.enums.accion import Accion
from core.domain.vo.mes import Mes
from finanzas.application.modificar_movimiento_use_case.dtos.modificar_movimiento_input_dto import (
    ModificarMovimientoInputDTO,
)
from finanzas.domain.events.movimiento_modificado_event import MovimientoModificadoEvent
from finanzas.domain.exceptions.movimiento_no_encontrado_exception import MovimientoNoEncontradoException
from finanzas.tests.fakes.mundo import HOGAR, OTRO_HOGAR, actor


def test_modificar_la_fecha_avisa_de_los_dos_meses_y_audita_solo_lo_que_cambia(mundo):
    m = mundo.movimiento(importe="-10", fecha=date(2026, 10, 1))
    entrada = ModificarMovimientoInputDTO(HOGAR, actor(), m.id, {"fecha": date(2026, 9, 30), "importe": Decimal("-11")})

    mundo.modificar.ejecutar(entrada)

    [evento] = mundo.eventos.publicados
    assert isinstance(evento, MovimientoModificadoEvent) and evento.meses == {Mes(2026, 9), Mes(2026, 10)}
    [(accion, _, _, _, cambios)] = mundo.auditoria.registros
    assert accion == Accion.MODIFICAR
    assert cambios == {"fecha": ["2026-10-01", "2026-09-30"], "importe": ["-10.00", "-11.00"]}


def test_modificar_un_movimiento_de_otro_hogar_es_no_encontrado(mundo):
    ajeno = mundo.movimiento(hogar_id=OTRO_HOGAR)
    with pytest.raises(MovimientoNoEncontradoException):
        mundo.modificar.ejecutar(ModificarMovimientoInputDTO(HOGAR, actor(), ajeno.id, {"concepto": "mío"}))
