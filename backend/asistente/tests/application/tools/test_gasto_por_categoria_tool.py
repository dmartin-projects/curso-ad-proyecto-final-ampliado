"""Módulo 94: gasto_por_categoria, sobre el fake de finanzas."""

from asistente.application.tools.gasto_por_categoria_tool import GastoPorCategoriaArgumentos, GastoPorCategoriaTool
from asistente.tests.fakes.consultas_de_finanzas_fake import ConsultasDeFinanzasFake, resumen
from asistente.tests.fakes.mundo import HOGAR, SEPTIEMBRE, contexto


def test_las_categorias_de_mayor_a_menor_con_su_porcentaje():
    finanzas = ConsultasDeFinanzasFake(
        {(HOGAR, SEPTIEMBRE): resumen(SEPTIEMBRE, gastos="1000", categorias=[("Supermercado", "600"), ("Ocio", "400")])}
    )
    r = GastoPorCategoriaTool(finanzas=finanzas).ejecutar(contexto(), GastoPorCategoriaArgumentos(mes="2026-09"))
    assert r == {
        "mes": "2026-09",
        "gastos": "1000.00",
        "categorias": [
            {"categoria": "Supermercado", "total": "600.00", "porcentaje": 60.0},
            {"categoria": "Ocio", "total": "400.00", "porcentaje": 40.0},
        ],
    }
