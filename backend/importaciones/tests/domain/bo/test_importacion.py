"""La importación y su ciclo de vida (módulo 88), sin base de datos."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from importaciones.domain.bo.fila import Fila
from importaciones.domain.bo.importacion import Importacion
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.exceptions.estado_no_permitido_exception import EstadoNoPermitidoException

E = EstadoImportacion


def importacion(estado=E.ANALIZANDO):
    return Importacion(
        hogar_id=1, cuenta_id=1, nombre_original="x.csv", formato="csv", huella_archivo="h", estado=estado
    )


def fila(dia, importe, accion=Accion.CREAR):
    return Fila(dia, date(2026, 10, dia), "X", Decimal(importe), f"h{dia}", accion)


def test_analizada_resume_la_vista_previa():
    imp = importacion()
    imp.analizada([fila(1, "-45.30", Accion.CONCILIAR), fila(2, "2100.00"), fila(3, "-1.50", Accion.DUPLICADA)], [])
    assert imp.estado == E.VISTA_PREVIA and (imp.total_filas, imp.duplicados) == (3, 1)
    assert imp.resumen == {
        "desde": "2026-10-01",
        "hasta": "2026-10-03",
        "gastos": "-46.80",
        "ingresos": "2100.00",
        "duplicadas": 1,
        "conciliar": 1,
        "a_importar": 2,
    }


def test_transiciones_y_progreso():
    imp = importacion(E.VISTA_PREVIA)
    imp.resumen = {"a_importar": 4}
    imp.confirmar()
    imp.procesadas = 3
    assert imp.progreso == 75
    with pytest.raises(EstadoNoPermitidoException):
        imp.confirmar()  # confirmar dos veces: 409
    with pytest.raises(EstadoNoPermitidoException):
        imp.deshacer()  # a medio importar, no
    imp.completar(datetime(2026, 10, 15, tzinfo=UTC))
    assert imp.progreso == 100
    imp.deshacer()
    assert imp.estado == E.DESHECHA
