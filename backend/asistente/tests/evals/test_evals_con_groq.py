"""Módulo 103: el golden set con Groq de verdad (grabado en cassettes) sobre la casa de los tests, con el juez (Qwen,
de otra familia que los modelos evaluados). Tres modelos, el mismo golden set: la comparación del §8.

    ASISTENTE_API_KEY=… PAUSA=45 uv run pytest asistente/tests/evals/test_evals_con_groq.py --record-mode=once -s

El primero es la PUERTA del CI: con el modelo de producción, ningún caso de la línea base puede dejar de aprobar.
Reproducido desde su cassette detecta las regresiones de nuestro código (un prompt, una tool, el bucle); grabado de
nuevo (el workflow semanal evals.yml), las del proveedor.
"""

import os
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest
import time_machine
import yaml

from asistente.application.agent.agente import Agente
from asistente.application.agent.limites import Limites
from asistente.application.evals.evaluacion import evaluar, informe, regresiones
from asistente.application.evals.juez import JuezLLM
from asistente.application.ports.i_llm import ILLM
from asistente.infrastructure import container
from asistente.management.commands.evaluar_asistente import casos

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave"), pytest.mark.django_db]

LINEA_BASE = yaml.safe_load((Path(__file__).parent / "linea_base.yaml").read_text())
JUEZ = "qwen/qwen3.8-27b"


class Pausado(ILLM):
    """Al grabar, una pausa antes de cada llamada (los tokens por minuto de la capa gratuita); al reproducir, ninguna."""

    def __init__(self, dentro: ILLM):
        self.dentro, self.segundos = dentro, float(os.environ.get("PAUSA", "0"))

    @property
    def modelo(self):
        return self.dentro.modelo

    def generar(self, peticion):
        time.sleep(self.segundos)
        return self.dentro.generar(peticion)


def golden(casa, modelo: str, juez: str = JUEZ) -> tuple[str, list]:
    ana, hogar = casa
    with time_machine.travel(datetime(2026, 10, 29, 10, 0, tzinfo=UTC), tick=False):
        contexto = container.contexto(ana.pk, hogar.pk)
        llm = Pausado(container.llm(modelo))  # solo ese modelo: sin reserva (diría otro el que contesta)
        resultados = evaluar(
            # Sin límite de tiempo: al grabar, las pausas (PAUSA) no son tiempo del modelo y harían saltar el de 60 s
            lambda: Agente(llm=llm, tools=container.tools(chat=True), limites=Limites(segundos=3600)),
            casos(),
            contexto,
            juez=JuezLLM(Pausado(container.llm(juez))),
        )
    salida = informe(resultados, con_ms=False)
    print(salida)
    return salida, resultados


def test_groq_la_puerta_gpt_oss_120b(casa):
    salida, resultados = golden(casa, "openai/gpt-oss-120b")
    assert regresiones(resultados, LINEA_BASE) == []
    if not os.environ.get("EVALS_EN_VIVO"):  # en vivo (evals.yml), el texto cambia: solo la puerta
        assert salida == SALIDA_120B


def test_groq_comparar_gpt_oss_20b(casa):
    salida, _ = golden(casa, "openai/gpt-oss-20b")
    assert salida == SALIDA_20B


def test_groq_comparar_qwen(casa):
    salida, _ = golden(casa, "qwen/qwen3.8-27b", juez="openai/gpt-oss-20b")  # un juez que no sea de su familia
    assert salida == SALIDA_QWEN


SALIDA_120B = """\
✓ gasto-septiembre         2 vueltas ·   5885 tokens · resumen_mes
✓ agosto-o-septiembre      3 vueltas ·   9125 tokens · resumen_mes, resumen_mes
✗ bar-manolo               2 vueltas ·   6107 tokens · buscar_movimientos
    contiene: no cumple ['(?i)\\\\b(3|tres)\\\\b']
✓ previsión                2 vueltas ·   7658 tokens · prevision_fin_de_mes
✓ sin-datos                2 vueltas ·   5873 tokens · resumen_mes
✓ fuera-de-su-terreno      1 vueltas ·   2939 tokens · sin tools
✓ apuntar-churros          2 vueltas ·   6699 tokens · proponer_movimiento

Aprobados 6 de 7 (86%)
Por grader: terminada 7/7 · cifras 2/2 · trayectoria 6/6 · contiene 2/3 · juez 5/5
Por categoría: cifras 1/1 · comparar 1/1 · buscar 0/1 · prevision 1/1 · honestidad 2/2 · accion 1/1
Tokens: 44286 en total · 6107 de mediana por pregunta · vueltas de mediana: 2
"""
SALIDA_20B = """\
✓ gasto-septiembre         2 vueltas ·   6062 tokens · resumen_mes
✓ agosto-o-septiembre      2 vueltas ·   6428 tokens · comparar_meses
✗ bar-manolo               2 vueltas ·   6144 tokens · buscar_movimientos
    contiene: no cumple ['(?i)\\\\b(3|tres)\\\\b']
✓ previsión                2 vueltas ·   6351 tokens · prevision_fin_de_mes
✓ sin-datos                2 vueltas ·   5948 tokens · resumen_mes
✗ fuera-de-su-terreno      1 vueltas ·   2962 tokens · sin tools
    juez: 3/5: La respuesta cumple la parte principal de la rúbrica al admitir que no puede saber el tiempo sin inventar nada. Sin embargo, le falta el segundo punto de la rúbrica: no ofrece lo que sí sabe hacer (ayudar con gastos, presupuestos o movimientos).
✗ apuntar-churros          2 vueltas ·   6414 tokens · proponer_movimiento
    contiene: no cumple ['(?i)confirm']
    juez: 2/5: La respuesta inventa opciones de categorías (Restaurantes u Ocio) que no se mencionan en la referencia ni en la rúbrica, lo cual constituye información falsa o inventada. Además, no cumple con el requisito principal de la rúbrica de indicar que la entrada está preparada y pendiente de confirmación, sino que pide más datos antes de proceder.

Aprobados 4 de 7 (57%)
Por grader: terminada 7/7 · cifras 2/2 · trayectoria 6/6 · contiene 1/3 · juez 3/5
Por categoría: cifras 1/1 · comparar 1/1 · buscar 0/1 · prevision 1/1 · honestidad 1/2 · accion 0/1
Tokens: 40309 en total · 6144 de mediana por pregunta · vueltas de mediana: 2
"""
SALIDA_QWEN = """\
✓ gasto-septiembre         2 vueltas ·   8318 tokens · resumen_mes
✓ agosto-o-septiembre      2 vueltas ·   8581 tokens · comparar_meses
✓ bar-manolo               3 vueltas ·  12964 tokens · buscar_movimientos, buscar_movimientos
✓ previsión                2 vueltas ·   8317 tokens · prevision_fin_de_mes
✓ sin-datos                2 vueltas ·   8292 tokens · resumen_mes
✓ fuera-de-su-terreno      1 vueltas ·   4102 tokens · sin tools
✓ apuntar-churros          2 vueltas ·   8390 tokens · proponer_movimiento

Aprobados 7 de 7 (100%)
Por grader: terminada 7/7 · cifras 2/2 · trayectoria 6/6 · contiene 3/3 · juez 5/5
Por categoría: cifras 1/1 · comparar 1/1 · buscar 1/1 · prevision 1/1 · honestidad 2/2 · accion 1/1
Tokens: 58964 en total · 8318 de mediana por pregunta · vueltas de mediana: 2
"""
