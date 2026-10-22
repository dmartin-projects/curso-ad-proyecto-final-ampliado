"""Contract tests (módulo 89): los MISMOS tests contra los command repositories de SQLAlchemy y contra los fakes.

Los tests de los use cases se fían de los fakes. Si un fake se porta distinto que PostgreSQL (deja que una
versión vieja pise a una nueva, no deshace un savepoint, acepta un importe que no cabe…), esos tests mienten.
Aquí se comprueba que no.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select

from estadisticas.domain.bo.membresia import Membresia
from estadisticas.domain.bo.movimiento import Movimiento
from estadisticas.domain.exceptions.evento_invalido_exception import EventoInvalidoException
from estadisticas.infrastructure.database.models.membresia_model import MembresiaModel
from estadisticas.infrastructure.database.models.movimiento_model import MovimientoModel
from estadisticas.infrastructure.database.models.progreso_model import ProgresoModel
from estadisticas.infrastructure.database.repositories.membresia_command_repository_sql import (
    MembresiaCommandRepositorySQL,
)
from estadisticas.infrastructure.database.repositories.movimiento_command_repository_sql import (
    MovimientoCommandRepositorySQL,
)
from estadisticas.infrastructure.database.repositories.progreso_command_repository_sql import (
    ProgresoCommandRepositorySQL,
)
from estadisticas.infrastructure.database.sesiones import sesion
from estadisticas.infrastructure.database.unidad_de_trabajo_sql import UnidadDeTrabajoSQL
from tests.fakes.mundo import Mundo

MARCA = datetime(2026, 10, 15, 12, 0, tzinfo=UTC)


@dataclass
class Entorno:
    uow: object
    movimientos: object
    membresias: object
    progreso: object
    importes: Callable[[], dict[int, Decimal]]  # lo que hay guardado, leído por fuera del repositorio
    roles: Callable[[], dict[tuple[int, int], str]]
    progresos: Callable[[], dict[tuple[str, int], int]]


@pytest.fixture(params=["memoria", "sql"])
def e(request) -> Entorno:
    if request.param == "memoria":
        m = Mundo()
        return Entorno(
            m.uow,
            m.movimientos,
            m.membresias,
            m.progreso,
            lambda: {pk: x.importe for pk, x in m.memoria.movimientos.items()},
            lambda: {k: x.rol for k, x in m.memoria.membresias.items()},
            lambda: {k: offset for k, (offset, _) in m.memoria.progreso.items()},
        )
    s = sesion()
    request.addfinalizer(s.close)

    def leer(*columnas):
        with sesion() as otra:  # otra sesión: solo ve lo CONFIRMADO
            return otra.execute(select(*columnas)).all()

    return Entorno(
        UnidadDeTrabajoSQL(s),
        MovimientoCommandRepositorySQL(s),
        MembresiaCommandRepositorySQL(s),
        ProgresoCommandRepositorySQL(s),
        lambda: dict(leer(MovimientoModel.id, MovimientoModel.importe)),
        lambda: {(h, u): r for h, u, r in leer(MembresiaModel.hogar_id, MembresiaModel.usuario_id, MembresiaModel.rol)},
        lambda: {(t, p): o for t, p, o in leer(ProgresoModel.topic, ProgresoModel.particion, ProgresoModel.offset)},
    )


def mov(pk: int = 7, importe: str = "-10.00", version: int = 1) -> Movimiento:
    return Movimiento(pk, 1, 1, date(2026, 10, 1), Decimal(importe), None, None, "manual", True, version)


def test_solo_gana_una_version_mas_nueva(e):
    with e.uow:
        assert e.movimientos.guardar(mov(importe="-10.00", version=5)) is True
        assert e.movimientos.guardar(mov(importe="-12.50", version=6)) is True
        assert e.movimientos.guardar(mov(importe="-12.50", version=6)) is False  # el mismo, otra vez
        assert e.movimientos.guardar(mov(importe="-99.00", version=2)) is False  # uno viejo que llega tarde
    assert e.importes() == {7: Decimal("-12.50")}


def test_borrar_solo_con_una_version_mas_nueva(e):
    with e.uow:
        e.movimientos.guardar(mov(version=5))
        assert e.movimientos.eliminar(7, version=3) is False  # tombstone viejo: no borra lo nuevo
        assert e.movimientos.eliminar(7, version=6) is True
        assert e.movimientos.eliminar(7, version=6) is False  # repetido
        assert e.movimientos.eliminar(8, version=1) is False  # no existía
    assert e.importes() == {}


def test_membresias(e):
    with e.uow:
        assert e.membresias.guardar(Membresia(1, 5, "lector", 1)) is True
        assert e.membresias.guardar(Membresia(1, 5, "admin", 2)) is True
        assert e.membresias.guardar(Membresia(1, 5, "lector", 1)) is False
        e.membresias.guardar(Membresia(1, 6, "lector", 3))
        assert e.membresias.eliminar(1, 6, version=1) is False
    assert e.roles() == {(1, 5): "admin", (1, 6): "lector"}
    with e.uow:
        assert e.membresias.eliminar(1, 6, version=4) is True
    assert e.roles() == {(1, 5): "admin"}


def test_progreso_por_particion(e):
    with e.uow:
        e.progreso.guardar("t", 0, 10, MARCA)
        e.progreso.guardar("t", 1, 3, MARCA)
        e.progreso.guardar("t", 0, 11, MARCA)
    assert e.progresos() == {("t", 0): 11, ("t", 1): 3}


def test_lo_que_no_cabe_es_un_evento_invalido_y_el_savepoint_deshace_solo_eso(e):
    with e.uow:
        e.movimientos.guardar(mov(1))
        with pytest.raises(EventoInvalidoException), e.uow.savepoint():
            e.movimientos.guardar(mov(2))  # dentro del savepoint: se deshace con él
            e.movimientos.guardar(mov(3, importe="99999999999.00"))  # Numeric(12, 2): no cabe
        e.movimientos.guardar(mov(4))  # la transacción sigue viva
    assert set(e.importes()) == {1, 4}


def test_la_unidad_de_trabajo_deshace_todo(e):
    with pytest.raises(RuntimeError), e.uow:
        e.movimientos.guardar(mov(1))
        e.membresias.guardar(Membresia(1, 5, "lector", 1))
        e.progreso.guardar("t", 0, 1, MARCA)
        raise RuntimeError("algo falla antes de confirmar")
    assert (e.importes(), e.roles(), e.progresos()) == ({}, {}, {})


def test_vaciar(e):
    with e.uow:
        e.movimientos.guardar(mov(1))
        e.membresias.guardar(Membresia(1, 5, "lector", 1))
        e.progreso.guardar("t", 0, 1, MARCA)
    with e.uow:
        e.movimientos.vaciar()
        e.membresias.vaciar()
        e.progreso.vaciar()
    assert (e.importes(), e.roles(), e.progresos()) == ({}, {}, {})
