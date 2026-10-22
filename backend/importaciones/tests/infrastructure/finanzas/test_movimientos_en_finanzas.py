"""Contract test de IMovimientos (módulo 88): el adapter hacia finanzas y su fake se portan igual."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from conftest import CuentaFactory, MovimientoFactory
from core.domain.vo.actor import Actor
from importaciones.application.ports.i_movimientos import IMovimientos
from importaciones.domain.bo.fila import Fila
from importaciones.domain.enums.accion import Accion
from importaciones.infrastructure.finanzas.movimientos_en_finanzas import MovimientosEnFinanzas
from importaciones.tests.fakes.movimientos_fake import MovimientosFake
from importaciones.tests.fakes.mundo import HOGAR, OTRO_HOGAR


@dataclass
class Entorno:
    movimientos: IMovimientos
    hogar: int
    otro_hogar: int
    cuenta: int
    gasto_a_mano: object  # (fecha, importe) → id de un movimiento sin huella en la cuenta


@pytest.fixture(params=["memoria", "orm"])
def entorno(request) -> Entorno:
    if request.param == "memoria":
        movimientos = MovimientosFake((HOGAR, 10))
        return Entorno(movimientos, HOGAR, OTRO_HOGAR, 10, lambda fecha, importe: movimientos.nuevo(10, fecha, importe))
    request.getfixturevalue("db")
    cuenta, ajena = CuentaFactory(), CuentaFactory()
    return Entorno(
        MovimientosEnFinanzas(),
        cuenta.hogar_id,
        ajena.hogar_id,
        cuenta.pk,
        lambda fecha, importe: MovimientoFactory(cuenta=cuenta, fecha=fecha, importe=importe).pk,
    )


def filas(*acciones) -> list[Fila]:
    return [Fila(n, date(2026, 10, n), f"F{n}", Decimal("-1"), f"f{n}", a) for n, a in enumerate(acciones, start=1)]


def test_movimientos_apuntar_conciliar_y_deshacer(entorno):
    m, sistema = entorno.movimientos, Actor.sistema()
    assert m.cuenta_del_hogar(entorno.hogar, entorno.cuenta) and not m.cuenta_del_hogar(
        entorno.otro_hogar, entorno.cuenta
    )
    a_mano = entorno.gasto_a_mano(date(2026, 10, 2), Decimal("-45.30"))
    assert [c.movimiento_id for c in m.candidatos(entorno.cuenta, date(2026, 10, 1), date(2026, 10, 5))] == [a_mano]

    ids = m.apuntar(
        hogar_id=entorno.hogar, actor=sistema, cuenta_id=entorno.cuenta, filas=filas(Accion.CREAR, Accion.CREAR)
    )
    assert len(ids) == 2 and m.huellas_existentes(entorno.cuenta, ["f1", "f2", "f9"]) == {"f1", "f2"}
    assert m.conciliar(hogar_id=entorno.hogar, actor=sistema, huellas={a_mano: "banco", ids[0]: "otra"}) == {a_mano}
    assert m.candidatos(entorno.cuenta, date(2026, 10, 1), date(2026, 10, 5)) == []  # ya tiene su fila del banco

    m.eliminar(hogar_id=entorno.hogar, actor=sistema, ids=ids)
    m.desconciliar(hogar_id=entorno.hogar, actor=sistema, ids=[a_mano])
    assert m.huellas_existentes(entorno.cuenta, ["f1", "f2", "banco"]) == set()
    assert [c.movimiento_id for c in m.candidatos(entorno.cuenta, date(2026, 10, 1), date(2026, 10, 5))] == [a_mano]
