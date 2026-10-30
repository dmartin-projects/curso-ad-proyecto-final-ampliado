"""Módulo 101: las tools del catálogo frente a text-to-SQL, con Groq de verdad (gpt-oss-120b, grabado) y PostgreSQL de
verdad (el rol del asistente, con su Row Level Security), sobre la casa de los tests.

    ASISTENTE_API_KEY=… uv run pytest asistente/tests/sql/test_comparar_con_groq.py --record-mode=once -s
"""

import re
from datetime import UTC, datetime

import pytest
import time_machine
import yaml

from asistente.infrastructure import container
from asistente.management.commands.comparar_sql_y_tools import PREGUNTAS, comparar

pytestmark = [
    pytest.mark.vcr,
    pytest.mark.usefixtures("clave", "rol_sql"),
    pytest.mark.django_db(transaction=True),  # la consulta del rol va por otra conexión: los datos, confirmados
]


def test_groq_las_mismas_preguntas_por_los_dos_caminos(casa, settings):
    settings.ASISTENTE_MODELOS_RESERVA = []  # si el principal no está, el cassette no se graba con otro modelo
    ana, hogar = casa
    with time_machine.travel(datetime(2026, 10, 29, 10, 0, tzinfo=UTC), tick=False):
        contexto = container.contexto(ana.pk, hogar.pk)
        salida = comparar(
            yaml.safe_load(PREGUNTAS.read_text()),
            contexto,
            {"tools": container.agente(), "sql": container.agente_sql()},
        )
    print(salida)
    assert re.sub(r"\b\d+ ms\b", "N ms", salida) == SALIDA


SALIDA = (
    "> ¿Cuánto gastamos en septiembre?\n"
    "  tools  ✓ 2 vueltas · 4074 tokens · N ms · ['resumen_mes']\n"
    "         «En septiembre gastasteis **776,59 €**. Detalle: los ingresos fueron 2 100,00 €, con un balance positivo de 1 323,41 €. Tuvisteis 10 movimientos y el gasto aumentó un 15,7 % respecto a agosto.»\n"
    "  sql    ✓ 2 vueltas · 1822 tokens · N ms · ['consultar_sql']\n"
    "         SQL: {\"sql\":\"SELECT -SUM(importe) AS total_gastado FROM movimientos WHERE date_trunc('month', fecha) = DATE '2026-09-01' AND importe \\u003c 0;\"}\n"
    "         «Gastasteis **776,59 €** en septiembre. Detalle: la suma de todos los importes negativos (gastos) del mes de septiembre de 2026 es 776,59 €.»\n"
    "> ¿En qué categoría gastamos más en septiembre?\n"
    "  tools  ✓ 2 vueltas · 4195 tokens · N ms · ['gasto_por_categoria']\n"
    "         «Gastasteis más en la categoría **Supermercado**. En septiembre de 2026 el gasto total fue 776,59 €, de los cuales 461,35 € (59,4 %) correspondieron a Supermercado, seguida de Restaurantes (102,00 €, 13,1 %).»\n"
    "  sql    ✓ 2 vueltas · 1766 tokens · N ms · ['consultar_sql']\n"
    "         SQL: {\"sql\":\"SELECT categoria AS categoria, SUM(importe) AS total_gasto\\nFROM movimientos\\nWHERE fecha \\u003e= DATE '2026-09-01' AND fecha \\u003c DATE '2026-10-01' AND importe \\u003c 0\\nGROUP BY categoria\\nORDER BY total_gasto ASC\\nLIMIT 1;\"}\n"
    "         «En septiembre gastasteis más en la categoría **Supermercado**, con un total de **461,35 €**. Detalle: el total de los importes negativos (gastos) de esa categoría en septiembre de 2026 fue -461,35 €, lo que representa la»\n"
    "> ¿Cuál ha sido nuestro gasto más grande de octubre?\n"
    "  tools  ✓ 2 vueltas · 4356 tokens · N ms · ['top_comercios']\n"
    "         «El mayor gasto de octubre fue en **Mercadona**, con un total de **301,25 €**. (En octubre los cinco comercios con más gasto fueron: Mercadona (301,25 €), Lidl (45,80 €), Renfe (37,50 €), Bar Manolo (31,20 €) y Netflix (1»\n"
    "  sql    ✓ 2 vueltas · 1918 tokens · N ms · ['consultar_sql']\n"
    "         SQL: {\"sql\":\"SELECT fecha, importe, concepto, categoria, comercio FROM movimientos WHERE fecha \\u003e= DATE '2026-10-01' AND fecha \\u003c= DATE '2026-10-31' AND importe \\u003c 0 ORDER BY importe ASC LIMIT 1;\"}\n"
    "         «El gasto más grande de octubre fue **301,25 €** (una compra semanal) en **Mercadona** el 3 de octubre. *Detalles:* importe = ‑301,25 €, categoría = Supermercado, concepto = Compra semanal.»\n"
    "> ¿Cuántas veces hemos ido al Bar Manolo?\n"
    "  tools  ✗ 2 vueltas · 4226 tokens · N ms · ['buscar_movimientos']\n"
    "         «Habéis ido al Bar Manolo **1 vez** este mes (31,20 € gastados).»\n"
    "  sql    ✓ 2 vueltas · 1550 tokens · N ms · ['consultar_sql']\n"
    '         SQL: {"sql":"SELECT COUNT(*) AS veces FROM movimientos WHERE comercio = \'Bar Manolo\';"}\n'
    "         «Habéis ido al Bar Manolo **3 veces**.»\n"
    "> ¿Qué día de la semana gastamos más este año?\n"
    "  tools  ✗ 1 vueltas · 2299 tokens · N ms · []\n"
    "         «Lo siento, pero con las herramientas disponibles no podemos calcular directamente cuál es el día de la semana en que gastáis más durante el año. Ninguna de ellas permite agrupar los movimientos por día de la semana, sólo»\n"
    "  sql    ✓ 2 vueltas · 2110 tokens · N ms · ['consultar_sql']\n"
    "         SQL: {\"sql\":\"SELECT EXTRACT(DOW FROM fecha) AS dow, SUM(importe) AS total FROM movimientos WHERE importe \\u003c 0 AND fecha \\u003e= DATE '2026-01-01' AND fecha \\u003c= DATE '2026-12-31' GROUP BY dow ORDER BY total ASC;\"}\n"
    "         «Gastasteis más los **sábados**. **Detalle:** Sumando todos los importes negativos (gastos) del año 2026, el total por día de la semana es: - Sábado (dow = 6): ‑851,60 € - Lunes (dow = 1): ‑567,50 € - Domingo (dow = 0): ‑»\n"
    "\n"
    "tools  3 de 5 correctas · 19150 tokens · 9 vueltas\n"
    "sql    5 de 5 correctas · 9166 tokens · 10 vueltas\n"
)
