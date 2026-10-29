"""Módulo 93: manage.py probar_llm con llamadas REALES a Groq, grabadas en cassettes (las salidas del módulo).

Sin red ni clave: cada test reproduce su cassette (tests/management/commands/cassettes/). La duración (ms) es la
única parte que cambia al reproducir: se compara sin ella.
"""

import re
from datetime import date
from io import StringIO

import pytest
import time_machine
from django.core.management import call_command

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave")]


def probar(*argumentos, **opciones) -> str:
    salida = StringIO()
    call_command("probar_llm", *argumentos, stdout=salida, no_color=True, **opciones)
    print(salida.getvalue())  # con -s, al grabar: la salida real que enseña el módulo
    return re.sub(r" · \d+ ms · ", " · N ms · ", salida.getvalue())


def test_groq_una_pregunta():
    assert probar("Explica qué es un presupuesto doméstico en una frase", ver_peticion=True) == SALIDAS["una"]


def test_groq_temperatura_alta():
    salida = probar("Inventa un nombre para una app de gastos del hogar. Solo el nombre.", veces=3, temperatura=1.5)
    assert salida == SALIDAS["temperatura"]


@pytest.mark.parametrize("esfuerzo", ["bajo", "alto"])
def test_groq_razonamiento(esfuerzo):
    pregunta = (
        "Un hogar gasta 1.240 € en agosto y 1.116 € en septiembre. ¿Qué variación porcentual hay? Solo el número."
    )
    assert probar(pregunta, esfuerzo=esfuerzo, ver_razonamiento=True) == SALIDAS[esfuerzo]


@time_machine.travel(date(2026, 10, 29))
def test_groq_structured_output():
    assert probar("ayer pagué 23,40 en el Mercadona con la tarjeta", estructurado=True) == SALIDAS["estructurado"]


@time_machine.travel(date(2026, 10, 29))
@pytest.mark.parametrize("modelo", ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"])
def test_groq_tres_modelos_la_misma_extraccion(modelo):  # ejercicio 2
    frase = "anteayer cené con Marta en el Bar Manolo, 46,80 € en efectivo, a medias"
    assert probar(frase, estructurado=True, modelo=modelo) == SALIDAS[modelo]


SALIDAS = {
    "una": (
        "{\n"
        '  "model": "openai/gpt-oss-120b",\n'
        '  "messages": [\n'
        "    {\n"
        '      "role": "system",\n'
        '      "content": "Responde en español, breve."\n'
        "    },\n"
        "    {\n"
        '      "role": "user",\n'
        '      "content": "Explica qué es un presupuesto doméstico en una frase"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Un presupuesto doméstico es un plan que registra y controla los ingresos y gastos de un hogar para gestionar sus finanzas de manera equilibrada.\n"
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 92, salida 71 (razonamiento 34) · 0.000056 $]\n"
    ),
    "temperatura": (
        "**CasaBalance**\n"
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 97, salida 80 (razonamiento 67) · 0.000063 $]\n"
        "¡HogarBudget!\n"
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 97, salida 53 (razonamiento 39) · 0.000046 $]\n"
        "GastoHogar.\n"
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 97, salida 80 (razonamiento 66) · 0.000063 $]\n"
    ),
    "bajo": (
        "(razonamiento) Need compute ((1126? wait) September 1116 vs August 1240. Variation = (1116-1240)/1240*100 = -124/1240*100 = -10%. Actually 124/1240=0.1 so -10%. Output only number. Probably -10.\n"
        "-10%\n"
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 113, salida 78 (razonamiento 66) · 0.000064 $]\n"
    ),
    "alto": (
        '(razonamiento) The user asks: "Un hogar gasta 1.240 € en agosto y 1.116 € en septiembre. ¿Qué variación porcentual hay? Solo el número." They want the percentage variation between the two amounts, presumably the change from August to September, expressed as a percent. They say "Solo el número." So we should give just the numeric result (maybe with sign? maybe just the absolute? Probably they want percent change: (new - old) / old * 100. So (1,116 - 1,240) / 1,240 * 100 = (-124) / 1240 * 100 = -10%. Actually compute: 1240 - 1116 = 124. So difference is -124 (decrease). Divided by 1240 = -0.1 => -10%. So the variation is -10%. If they want just the number, perhaps "-10". They might want "10%"? The phrasing "¿Qué variación porcentual hay? Solo el número." Usually they might want the percentage change magnitude: -10% (decrease). Since they ask "variación porcentual", it\'s typical to include sign. They say "Solo el número." Possibly just "-10". But might need to include the percent sign? They said "solo el número". So I think we should output "-10%"? However that includes the percent sign, not just number. But the percent sign might be considered part of the answer. Usually they\'d want the number value. I\'d respond with "-10". Could also say "-10%". But they explicitly say "Solo el número." So I\'d give "-10". In Spanish: I\'d say "-10". The answer: -10. Also could be "–10". Let\'s give -10.\n'
        "-10\n"
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 113, salida 380 (razonamiento 369) · 0.000245 $]\n"
    ),
    "estructurado": (
        '{"concepto": "Mercadona", "importe": "-23.40", "fecha": "2026-10-28", "cuenta": "Tarjeta"}\n'
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 340, salida 251 (razonamiento 209) · 0.000202 $]\n"
    ),
    "openai/gpt-oss-120b": (
        '{"concepto": "Bar Manolo", "importe": "-23.40", "fecha": "2026-10-27", "cuenta": "Efectivo"}\n'
        "  [openai/gpt-oss-120b · N ms · fin · tokens: entrada 348, salida 414 (razonamiento 370) · 0.000301 $]\n"
    ),
    "openai/gpt-oss-20b": (
        '{"concepto": "Bar Manolo", "importe": "-46.80", "fecha": "2026-10-27", "cuenta": "Efectivo"}\n'
        "  [openai/gpt-oss-20b · N ms · fin · tokens: entrada 348, salida 466 (razonamiento 422) · 0.000166 $]\n"
    ),
    "qwen/qwen3.8-27b": (
        '{"concepto": "Cena Bar Manolo con Marta", "importe": "23.40", "fecha": "2026-10-27", "cuenta": "Efectivo"}\n'
        "  [qwen/qwen3.8-27b · N ms · fin · tokens: entrada 65, salida 49 (razonamiento 0) · 0.000248 $]\n"
    ),
}
