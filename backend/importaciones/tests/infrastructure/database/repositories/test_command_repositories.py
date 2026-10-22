"""Contract tests de las importaciones (módulo 88): el repositorio, contra el ORM y contra el fake."""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from conftest import CuentaFactory, MovimientoFactory
from importaciones.domain.bo.fila import Fila
from importaciones.domain.bo.importacion import Importacion
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.exceptions.extracto_repetido_exception import ExtractoRepetidoException
from importaciones.domain.exceptions.importacion_no_encontrada_exception import ImportacionNoEncontradaException
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository
from importaciones.infrastructure.database.repositories.importacion_command_repository_orm import (
    ImportacionCommandRepositoryORM,
)
from importaciones.tests.fakes.importacion_command_repository_fake import ImportacionCommandRepositoryFake
from importaciones.tests.fakes.mundo import HOGAR, OTRO_HOGAR

E = EstadoImportacion
AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)


@dataclass
class Entorno:
    importaciones: IImportacionCommandRepository
    hogar: int
    otro_hogar: int
    cuenta: int
    gasto_a_mano: object  # (fecha, importe) → id de un movimiento sin huella en la cuenta
    contenido: object


@pytest.fixture(params=["memoria", "orm"])
def entorno(request) -> Entorno:
    if request.param == "memoria":
        return Entorno(
            ImportacionCommandRepositoryFake(), HOGAR, OTRO_HOGAR, 10, lambda fecha, importe: 1000, lambda: b"csv"
        )
    request.getfixturevalue("db")
    cuenta, ajena = CuentaFactory(), CuentaFactory()
    return Entorno(
        ImportacionCommandRepositoryORM(),
        cuenta.hogar_id,
        ajena.hogar_id,
        cuenta.pk,
        lambda fecha, importe: MovimientoFactory(cuenta=cuenta, fecha=fecha, importe=importe).pk,
        lambda: SimpleUploadedFile("x.csv", b"csv", content_type="text/csv"),
    )


def nueva(e: Entorno, huella="h1") -> Importacion:
    i = Importacion(hogar_id=e.hogar, cuenta_id=e.cuenta, nombre_original="x.csv", formato="csv", huella_archivo=huella)
    e.importaciones.crear(i, e.contenido())
    return i


def filas(*acciones) -> list[Fila]:
    return [Fila(n, date(2026, 10, n), f"F{n}", Decimal("-1"), f"f{n}", a) for n, a in enumerate(acciones, start=1)]


def test_crear_obtener_y_repetido_solo_si_esta_activa(entorno):
    i = nueva(entorno)
    assert entorno.importaciones.obtener(entorno.hogar, i.id).estado == E.PENDIENTE
    with pytest.raises(ImportacionNoEncontradaException):
        entorno.importaciones.obtener(entorno.otro_hogar, i.id)
    with pytest.raises(ExtractoRepetidoException):
        nueva(entorno)
    assert entorno.importaciones.fallar(i.id, "roto", AHORA) == "csv"
    assert entorno.importaciones.fallar(i.id, "otra vez", AHORA) is None  # ya había terminado
    assert nueva(entorno).id != i.id  # la anterior falló: el mismo extracto se puede volver a subir


def test_reclamar_y_guardar(entorno):
    i = nueva(entorno)
    assert entorno.importaciones.reclamar(i.id, de=E.PENDIENTE, a=E.ANALIZANDO) is True
    assert entorno.importaciones.reclamar(i.id, de=E.PENDIENTE, a=E.ANALIZANDO) is False
    i = entorno.importaciones.por_id(i.id)
    i.analizada(filas(Accion.CREAR), [{"linea": 3, "mensaje": "x"}])
    entorno.importaciones.guardar(i)
    leida = entorno.importaciones.por_id(i.id)
    assert (leida.estado, leida.total_filas, leida.avisos) == (E.VISTA_PREVIA, 1, [{"linea": 3, "mensaje": "x"}])


def test_filas_separar_pendientes_y_contadores(entorno):
    i = nueva(entorno)
    gasto = entorno.gasto_a_mano(date(2026, 10, 1), Decimal("-1"))
    nuevas = filas(Accion.CREAR, Accion.CONCILIAR, Accion.DUPLICADA, Accion.CONCILIAR)
    nuevas[1].coincide_con_id = nuevas[3].coincide_con_id = gasto
    entorno.importaciones.crear_filas(i.id, nuevas)
    a_importar = entorno.importaciones.filas_a_importar(i.id)
    assert sorted(a_importar) == sorted(f.id for f in nuevas if f.accion != Accion.DUPLICADA)

    entorno.importaciones.separar(i.id, [nuevas[3].id])
    pendientes = entorno.importaciones.filas_pendientes(i.id, a_importar)
    assert [(f.numero, f.accion, f.coincide_con_id) for f in pendientes] == [
        (1, Accion.CREAR, None),
        (2, Accion.CONCILIAR, gasto),
        (4, Accion.CREAR, None),  # separada: se importará como un movimiento nuevo
    ]
    pendientes[1].movimiento_id = gasto
    entorno.importaciones.guardar_filas(pendientes)
    assert [f.numero for f in entorno.importaciones.filas_pendientes(i.id, a_importar)] == [1, 4]
    assert entorno.importaciones.movimientos(i.id, Accion.CONCILIAR) == [gasto]

    entorno.importaciones.sumar(i.id, procesadas=2, creados=1, conciliados=1, duplicados=0)
    entorno.importaciones.sumar(i.id, procesadas=1, creados=1, conciliados=0, duplicados=1)
    leida = entorno.importaciones.por_id(i.id)
    assert (leida.procesadas, leida.creados, leida.conciliados, leida.duplicados) == (3, 2, 1, 1)
