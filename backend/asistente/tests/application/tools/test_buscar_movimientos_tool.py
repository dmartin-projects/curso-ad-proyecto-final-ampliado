"""Módulo 95: buscar_movimientos devuelve el total y la suma de TODOS, y unos pocos como ejemplo."""

import pytest

from asistente.application.tools.buscar_movimientos_tool import BuscarMovimientosArgumentos, BuscarMovimientosTool
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.tests.fakes.mundo import contexto


def buscar(mundo, **args) -> dict:
    return BuscarMovimientosTool(finanzas=mundo.finanzas).ejecutar(contexto(), BuscarMovimientosArgumentos(**args))


def test_la_suma_de_todos_aunque_solo_se_vean_unos_pocos(mundo):
    r = buscar(mundo, texto="mercadona", desde="2026-08-01", limite=2)
    assert (r["periodo"], r["total"], r["suma_gastos"], r["suma_ingresos"]) == (
        "2026-08-01 a 2026-10-29",
        5,
        "1121.05",
        "0.00",
    )
    assert r["movimientos"] == [
        {
            "fecha": "2026-10-03",
            "importe": "-301.25",
            "concepto": "Compra semanal",
            "categoria": "Supermercado",
            "comercio": "Mercadona",
        },
        {
            "fecha": "2026-09-19",
            "importe": "-121.35",
            "concepto": "Compra",
            "categoria": "Supermercado",
            "comercio": "Mercadona",
        },
    ]
    assert r["sin_mostrar"] == 3


def test_una_categoria_principal_incluye_sus_hijas_y_sin_campos_vacios(mundo):
    r = buscar(mundo, categoria="casa", desde="2026-09-01", hasta="2026-09-30")  # Casa: incluye Luz
    assert (r["total"], r["suma_gastos"]) == (1, "92.75")
    assert r["movimientos"] == [
        {"fecha": "2026-09-28", "importe": "-92.75", "concepto": "Factura de la luz", "categoria": "Luz"}
    ]
    assert "sin_mostrar" not in r


def test_una_categoria_que_no_es_del_hogar_es_un_error_con_las_que_hay(mundo):
    with pytest.raises(ToolException) as e:
        buscar(mundo, categoria="Gimnasio")
    assert str(e.value) == (
        "No hay ninguna categoría «Gimnasio» en este hogar. Las que hay: Casa, Luz, Nómina, Ocio, Restaurantes, "
        "Supermercado, Transporte."
    )
    assert [c[0] for c in mundo.finanzas.consultas] == []  # ni se buscó


def test_solo_ingresos(mundo):
    r = buscar(mundo, tipo="ingreso", desde="2026-08-01")
    assert (r["total"], r["suma_gastos"], r["suma_ingresos"]) == (3, "0.00", "6300.00")


def test_la_categoria_como_la_escribe_el_usuario(mundo):
    """Sin mayúsculas ni tildes: 'nomina' es 'Nómina'."""
    r = buscar(mundo, categoria=" nomina", desde="2026-08-01")
    assert (r["total"], r["suma_ingresos"]) == (3, "6300.00")
