"""Módulo 103, ejercicios: pass@k y pass^k, el juez calibrado con juicios humanos (kappa) y la comparación de dos
respuestas en los dos órdenes, con un juez falso que siempre prefiere la primera."""

import json
from pathlib import Path

import pytest
import yaml

from asistente.application.agent.agente import Agente
from asistente.application.evals.calibrar_juez import calibrar, kappa
from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.comparar_respuestas import comparar
from asistente.application.evals.estabilidad import estabilidad, informe_de_estabilidad
from asistente.application.evals.juez import JuezLLM
from asistente.application.prompts.comparar import COMPARAR
from asistente.application.prompts.versiones import PUBLICADAS
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import HOGAR, SEPTIEMBRE, contexto

JUICIOS = yaml.safe_load((Path(__file__).parent / "juicios_humanos.yaml").read_text())
SEPT = CasoDeEval("gasto-septiembre", "¿Cuánto en septiembre?", "cifras", cifras=("776,59",))


# ── Ejercicio 1 ──
def test_un_caso_que_a_veces_si_y_a_veces_no_es_inestable(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    respuestas = iter(["776,59 €.", "Unos 700 €.", "776,59 €."])
    aprobadas = estabilidad(
        lambda: Agente(llm=LLMFake([LLMFake.responder(next(respuestas))]), tools=mundo.tools()), [SEPT], contexto(), 3
    )
    assert aprobadas == {"gasto-septiembre": 2}
    assert informe_de_estabilidad(aprobadas, 3) == (
        "gasto-septiembre         2/3  inestable ⚠\npass@3: 1/1 (100%) · pass^3: 0/1 (0%)\n"
    )


# ── Ejercicio 2 ──
def test_kappa_descuenta_el_acuerdo_por_azar():
    humano = [True] * 8 + [False] * 2
    assert kappa(humano, [True] * 10) == 0  # dice "bien" a todo: 80 % de acuerdo y ninguna información
    assert kappa(humano, humano) == 1
    assert kappa([True, False, True, False], [False, True, False, True]) == -1  # al revés, siempre


def test_calibrar_cuenta_las_coincidencias_con_la_persona():
    # un juez que aprueba todo lo que lee
    veredictos = [LLMFake.responder(json.dumps({"razonamiento": "Bien.", "puntuacion": 5})) for _ in JUICIOS]
    salida = calibrar(JuezLLM(LLMFake(veredictos)), JUICIOS)
    assert salida.splitlines()[-1] == "Acuerdo 5 de 10 · kappa de Cohen 0.00"


# ── Ejercicio 3 ──
def test_un_juez_que_siempre_prefiere_la_primera_queda_en_inconsistente():
    siempre_a = [LLMFake.responder(json.dumps({"razonamiento": "La primera.", "mejor": "A"})) for _ in range(2)]
    assert comparar(LLMFake(siempre_a), "¿?", "rúbrica", "corta", "larga") == "inconsistente"


@pytest.mark.parametrize(
    ("ida", "vuelta", "resultado"),
    [("A", "B", "primera"), ("B", "A", "segunda"), ("empate", "empate", "empate"), ("A", "empate", "inconsistente")],
)
def test_lo_que_dicen_los_dos_ordenes(ida, vuelta, resultado):
    guion = [LLMFake.responder(json.dumps({"razonamiento": "x", "mejor": m})) for m in (ida, vuelta)]
    assert comparar(LLMFake(guion), "¿?", "r", "una", "otra") == resultado


def test_el_prompt_de_comparar_esta_publicado():
    assert PUBLICADAS[(COMPARAR.nombre, COMPARAR.version)] == COMPARAR.huella
