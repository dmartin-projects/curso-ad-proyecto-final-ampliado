"""Módulo 94: manage.py preguntar, el agente completo con Groq de verdad (grabado en cassettes) y la base de datos.

Los datos del hogar son fijos (fixture `casa`) y el día también: la petición al modelo sale idéntica a la grabada.
"""

import re
from datetime import UTC, datetime
from io import StringIO

import pytest
import time_machine
from django.core.management import call_command
from django.core.management.base import CommandError

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave")]


@pytest.fixture(autouse=True)
def hoy():
    with time_machine.travel(datetime(2026, 10, 29, 10, 0, tzinfo=UTC), tick=False):
        yield


def preguntar(casa, pregunta, **opciones) -> str:
    ana, hogar = casa
    salida = StringIO()
    call_command("preguntar", pregunta, email=ana.email, hogar=hogar.pk, stdout=salida, no_color=True, **opciones)
    print(salida.getvalue())  # con -s, al grabar: la salida real que enseña el módulo
    return re.sub(r"\b\d+ ms\b", "N ms", salida.getvalue())


def test_groq_cuanto_y_en_que(casa):
    salida = preguntar(casa, "¿Cuánto gastamos en septiembre y en qué categoría se fue más dinero?")
    assert salida == SALIDAS["cuanto_y_en_que"]


def test_groq_comparar_dos_meses(casa):
    salida = preguntar(casa, "¿En qué categoría gastamos más en septiembre que en agosto?", resultados=True)
    assert salida == SALIDAS["comparar"]


def test_groq_un_mes_que_no_ha_empezado(casa):
    salida = preguntar(casa, "Dame el resumen de diciembre de 2026")
    assert salida == SALIDAS["futuro"]


def test_groq_tools_en_paralelo_con_qwen(casa):  # ejercicio 2: un modelo que pide varias tools en el mismo turno
    salida = preguntar(casa, "¿En qué categoría gastamos más en septiembre que en agosto?", modelo="qwen/qwen3.8-27b")
    assert salida == SALIDAS["paralelo"]


def test_quien_no_es_miembro_no_pregunta(casa, db):
    from conftest import UsuarioFactory

    ajeno = UsuarioFactory(email="ajeno@example.com")
    with pytest.raises(CommandError, match="El hogar no existe o no eres miembro"):
        call_command("preguntar", "¿Cuánto gastamos?", email=ajeno.email, hogar=casa[1].pk)


def test_un_email_que_no_existe(db):
    with pytest.raises(CommandError, match="No hay ningún usuario con el email nadie@example.com"):
        call_command("preguntar", "¿Cuánto gastamos?", email="nadie@example.com", hogar=1)


SALIDAS = {
    "cuanto_y_en_que": (
        "vuelta 1 · openai/gpt-oss-120b · N ms · tools · entrada 421, salida 82\n"
        '  → resumen_mes {"mes":"2026-09"}\n'
        "  ← resumen_mes (N ms): 152 caracteres\n"
        "vuelta 2 · openai/gpt-oss-120b · N ms · tools · entrada 506, salida 40\n"
        '  → gasto_por_categoria {"mes":"2026-09"}\n'
        "  ← gasto_por_categoria (N ms): 348 caracteres\n"
        "vuelta 3 · openai/gpt-oss-120b · N ms · fin · entrada 648, salida 92\n"
        "En septiembre gastamos **776,59\u202f€**. La categoría con mayor gasto fue **Supermercado**, con **461,35\u202f€** (≈\u202f59\u202f% del total).\n"
        "  [fin · 3 vueltas · 2 tool calls · N ms · tokens: entrada 1575, salida 214 (razonamiento 108) · 0.000364 $]\n"
    ),
    "comparar": (
        "vuelta 1 · openai/gpt-oss-120b · N ms · tools · entrada 419, salida 176\n"
        '  → gasto_por_categoria {"mes":"2026-09"}\n'
        '  ← gasto_por_categoria (N ms): {"mes":"2026-09","gastos":"776.59","categorias":[{"categoria":"Supermercado","total":"461.35","porcentaje":59.4},{"categoria":"Restaurantes","total":"102.00","porcentaje":13.1},{"categoria":"Casa","total":"92.75","porcentaje":11.9},{"categoria":"Ocio","total":"82.99","porcentaje":10.7},{"categoria":"Transporte","total":"37.50","porcentaje":4.8}]}\n'
        "vuelta 2 · openai/gpt-oss-120b · N ms · tools · entrada 561, salida 112\n"
        '  → gasto_por_categoria {"mes":"2026-08"}\n'
        '  ← gasto_por_categoria (N ms): {"mes":"2026-08","gastos":"671.35","categorias":[{"categoria":"Supermercado","total":"474.75","porcentaje":70.7},{"categoria":"Casa","total":"88.30","porcentaje":13.2},{"categoria":"Restaurantes","total":"46.80","porcentaje":7.0},{"categoria":"Transporte","total":"37.50","porcentaje":5.6},{"categoria":"Ocio","total":"24.00","porcentaje":3.6}]}\n'
        "vuelta 3 · openai/gpt-oss-120b · N ms · fin · entrada 703, salida 327\n"
        "En septiembre gastamos **más** que en agosto en:\n"
        "\n"
        "- **Restaurantes**: 102,00\u202f€ (vs 46,80\u202f€ en agosto)  \n"
        "- **Casa**: 92,75\u202f€ (vs 88,30\u202f€ en agosto)  \n"
        "- **Ocio**: 82,99\u202f€ (vs 24,00\u202f€ en agosto)  \n"
        "\n"
        "En las demás categorías (Supermercado y Transporte) el gasto fue menor o igual.\n"
        "  [fin · 3 vueltas · 2 tool calls · N ms · tokens: entrada 1683, salida 615 (razonamiento 446) · 0.000621 $]\n"
    ),
    "futuro": (
        "vuelta 1 · openai/gpt-oss-120b · N ms · tools · entrada 416, salida 65\n"
        '  → resumen_mes {"mes":"2026-12"}\n'
        '  ← resumen_mes (N ms): {"error": "El mes 2026-12 todavía no ha empezado (hoy es 2026-10-29). Pide un mes hasta 2026-10."}\n'
        "vuelta 2 · openai/gpt-oss-120b · N ms · fin · entrada 485, salida 125\n"
        "Lo siento, todavía no hay datos para diciembre de 2026 (aún no ha empezado el mes). ¿Te gustaría el resumen de octubre de 2026 o de algún mes anterior?\n"
        "  [fin · 2 vueltas · 1 tool calls · N ms · tokens: entrada 901, salida 190 (razonamiento 110) · 0.000249 $]\n"
    ),
    "paralelo": (
        "vuelta 1 · qwen/qwen3.8-27b · N ms · tools · entrada 613, salida 68\n"
        '  → gasto_por_categoria {"mes":"2026-09"}\n'
        "  ← gasto_por_categoria (N ms): 348 caracteres\n"
        '  → gasto_por_categoria {"mes":"2026-08"}\n'
        "  ← gasto_por_categoria (N ms): 345 caracteres\n"
        "vuelta 2 · qwen/qwen3.8-27b · N ms · fin · entrada 960, salida 165\n"
        "En septiembre gastaste más que en agosto sobre todo en:\n"
        "\n"
        "- **Ocio**: 82,99 € vs 24,00 € (+58,99 €)\n"
        "- **Restaurantes**: 102,00 € vs 46,80 € (+55,20 €)\n"
        "- **Casa**: 92,75 € vs 88,30 € (+4,45 €)\n"
        "- **Transporte**: igual (37,50 €)\n"
        "\n"
        "Y menos en **Supermercado**: 461,35 € vs 474,75 € (−13,40 €).\n"
        "\n"
        "¿Quieres el desglose por subcategorías de alguna de ellas?\n"
        "  [fin · 2 vueltas · 2 tool calls · N ms · tokens: entrada 1573, salida 233 (razonamiento 0) · 0.002190 $]\n"
    ),
}
