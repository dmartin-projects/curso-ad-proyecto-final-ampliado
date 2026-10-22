"""EliminarMovimientosUseCase con los fakes (módulo 88): borrar en bloque."""

from datetime import date

import pytest

from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.mes import Mes
from finanzas.application.eliminar_movimientos_use_case.dtos.eliminar_movimientos_input_dto import (
    EliminarMovimientosInputDTO,
)
from finanzas.domain.events.movimientos_eliminados_event import MovimientosEliminadosEvent
from finanzas.tests.fakes.mundo import HOGAR, OTRO_HOGAR, actor


def test_eliminar_varios_exige_admin_audita_y_publica(mundo):
    viejo, nuevo = mundo.movimiento(fecha=date(2026, 9, 1)), mundo.movimiento()
    ajeno = mundo.movimiento(hogar_id=OTRO_HOGAR)
    entrada = EliminarMovimientosInputDTO(HOGAR, actor(Rol.MIEMBRO), (viejo.id, nuevo.id, ajeno.id))
    with pytest.raises(SinPermisoException):
        mundo.eliminar_varios.ejecutar(entrada)

    borrados = mundo.eliminar_varios.ejecutar(EliminarMovimientosInputDTO(HOGAR, actor(Rol.ADMIN), entrada.ids))

    assert borrados == [viejo.id, nuevo.id] and len(mundo.movimientos.todos()) == 1
    assert [(r[0], r[2]) for r in mundo.auditoria.registros] == [(Accion.BORRAR, viejo.id), (Accion.BORRAR, nuevo.id)]
    assert mundo.eventos.publicados == [
        MovimientosEliminadosEvent(HOGAR, (viejo.id, nuevo.id), frozenset({Mes(2026, 9), Mes(2026, 10)}))
    ]
