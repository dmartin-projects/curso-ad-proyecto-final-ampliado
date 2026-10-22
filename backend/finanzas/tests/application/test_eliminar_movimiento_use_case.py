"""EliminarMovimientoUseCase con los fakes (módulo 87)."""

import pytest

from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.mes import Mes
from finanzas.application.eliminar_movimiento_use_case.dtos.eliminar_movimiento_input_dto import (
    EliminarMovimientoInputDTO,
)
from finanzas.domain.events.movimiento_eliminado_event import MovimientoEliminadoEvent
from finanzas.tests.fakes.mundo import HOGAR, actor


def test_eliminar_exige_admin_y_publica_el_tombstone(mundo):
    m = mundo.movimiento()
    with pytest.raises(SinPermisoException):
        mundo.eliminar.ejecutar(EliminarMovimientoInputDTO(HOGAR, actor(Rol.MIEMBRO), m.id))

    mundo.eliminar.ejecutar(EliminarMovimientoInputDTO(HOGAR, actor(Rol.ADMIN), m.id))

    assert mundo.movimientos.todos() == []
    assert mundo.eventos.publicados == [MovimientoEliminadoEvent(m.id, HOGAR, Mes(2026, 10))]
    assert mundo.auditoria.registros[0][0] == Accion.BORRAR
