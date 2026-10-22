"""RegistrarMovimientoUseCase con los fakes (módulo 87).

Lo que se prueba aquí es la ORQUESTACIÓN: quién puede, qué se guarda, qué se audita, qué se publica y que todo
vaya en una transacción. Que el ORM, la API o el outbox funcionen es cosa de tests/infrastructure.
"""

from datetime import date
from decimal import Decimal

import pytest

from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.domain.events.movimiento_registrado_event import MovimientoRegistradoEvent
from finanzas.domain.exceptions.categoria_no_encontrada_exception import CategoriaNoEncontradaException
from finanzas.domain.exceptions.cuenta_no_encontrada_exception import CuentaNoEncontradaException
from finanzas.domain.exceptions.fecha_futura_exception import FechaFuturaException
from finanzas.tests.fakes.mundo import HOGAR, HOY, actor


def registrar(mundo, rol=Rol.MIEMBRO, **cambios):
    datos = {"cuenta_id": 10, "fecha": HOY, "importe": Decimal("-30"), "concepto": "MERCADONA SA 0042"}
    return mundo.registrar.ejecutar(RegistrarMovimientoInputDTO(hogar_id=HOGAR, actor=actor(rol), **datos | cambios))


def test_registrar_guarda_audita_y_publica_en_una_transaccion(mundo):
    m = registrar(mundo, etiquetas=["Casa ", "casa"])

    [guardado] = mundo.movimientos.todos()
    assert (guardado.id, guardado.comercio_id, guardado.etiquetas) == (m.id, 100, ["casa"])  # Mercadona reconocido
    assert guardado.creado_por_id == 7
    assert mundo.auditoria.registros == [(Accion.CREAR, "finanzas.movimiento", m.id, 7, {})]
    assert [type(e) for e in mundo.eventos.publicados] == [MovimientoRegistradoEvent]
    assert mundo.uow.confirmadas == 1


@pytest.mark.parametrize(
    "cambios, error",
    [
        ({"cuenta_id": 20}, CuentaNoEncontradaException),  # la cuenta 20 es de OTRO hogar
        ({"categoria_id": 999}, CategoriaNoEncontradaException),
        ({"fecha": date(2026, 10, 16)}, FechaFuturaException),
    ],
)
def test_registrar_rechaza_y_no_deja_nada(mundo, cambios, error):
    with pytest.raises(error) as e:
        registrar(mundo, **cambios)
    assert e.value.campo  # todos son errores de un campo del formulario (400 en la API)
    assert mundo.movimientos.todos() == [] and mundo.eventos.publicados == [] and mundo.auditoria.registros == []


def test_un_lector_no_puede_registrar(mundo):
    with pytest.raises(SinPermisoException):
        registrar(mundo, rol=Rol.LECTOR)
    assert mundo.uow.confirmadas == mundo.uow.deshechas == 0  # ni siquiera abre la transacción


def test_si_falla_la_auditoria_no_queda_ni_movimiento_ni_evento(mundo):
    mundo.auditoria.fallar = True
    with pytest.raises(RuntimeError):
        registrar(mundo)
    assert mundo.uow.deshechas == 1
    assert mundo.movimientos.todos() == [] and mundo.eventos.publicados == []  # todo o nada (módulo 85)
