"""Módulo 84, ejercicio 1: las métricas de negocio de las importaciones."""

import pytest

from .conftest import CSV_BANCO_A
from .test_api import en_commit, escenario, subir, url  # noqa: F401 (fixtures)

pytestmark = pytest.mark.django_db
TOTAL, MOVIMIENTOS = "gastos.importaciones", "gastos.importaciones.movimientos"
CSV_OK = (("estado", "completada"), ("formato", "csv"))
CSV_ERROR = (("estado", "error"), ("formato", "csv"))


def test_una_importacion_completada_suma_y_registra_sus_movimientos(
    telemetria,
    escenario,  # noqa: F811 (fixture de test_api)
    subir,  # noqa: F811
    cliente,
    en_commit,  # noqa: F811
):
    hogar, roles, cuenta = escenario
    # (en producción las series existen desde el arranque, a 0; en los tests, el proveedor de métricas se
    # configura después de importar el módulo y esos add(0) se pierden: de ahí el .get(…, 0))
    antes = telemetria.metrica(TOTAL).get(CSV_OK, 0)
    movimientos = telemetria.metrica(MOVIMIENTOS).get((("formato", "csv"),), 0)

    imp = subir(hogar, roles["miembro"], cuenta, CSV_BANCO_A).data
    en_commit(cliente(roles["miembro"]).post, url(hogar, f"{imp['id']}/confirmar/"), {})

    assert telemetria.metrica(TOTAL)[CSV_OK] == antes + 1
    assert telemetria.metrica(MOVIMIENTOS)[(("formato", "csv"),)] == movimientos + 5  # 5 filas nuevas


def test_una_importacion_fallida_cuenta_como_error(telemetria, escenario, subir):  # noqa: F811 (fixtures)
    hogar, roles, cuenta = escenario
    antes = telemetria.metrica(TOTAL).get(CSV_ERROR, 0)

    subir(hogar, roles["miembro"], cuenta, b"nombre;edad\nana;30\n")

    assert telemetria.metrica(TOTAL)[CSV_ERROR] == antes + 1
