"""Módulo 103: la evaluación y el juez con un LLMFake (sin red): que el golden set se lea, que cada caso se califique
con lo suyo, que el juez puntúe con su schema y que la puerta del CI vea las regresiones."""

import json

from asistente.application.agent.agente import Agente
from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.evaluacion import evaluar, informe, regresiones
from asistente.application.evals.juez import ESQUEMA, JuezLLM
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.management.commands.evaluar_asistente import casos
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import HOGAR, SEPTIEMBRE, contexto

SEPT = CasoDeEval(
    "gasto-septiembre", "¿Cuánto gastamos en septiembre?", "cifras", cifras=("776,59",), alguna_de=("resumen_mes",)
)
CON_RUBRICA = CasoDeEval(
    "sin-datos", "¿Cuánto en diciembre de 2025?", "honestidad", rubrica="Dice que no hay gastos.", referencia="No hay."
)


def veredicto(puntuacion: int, razon: str = "Cumple la rúbrica.") -> LLMFake:
    return LLMFake.responder(json.dumps({"razonamiento": razon, "puntuacion": puntuacion}))


def test_el_golden_set_se_lee_entero_y_sin_ids_repetidos():
    todos = casos()
    assert len(todos) == 7 and len({c.id for c in todos}) == 7
    assert casos(["bar-manolo"])[0].contiene == (r"(?i)\b(3|tres)\b",)


def test_cada_caso_con_su_agente_y_sus_graders(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    guiones = iter(
        [
            [LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("Gastasteis 776,59 €.")],
            [LLMFake.responder("Gastasteis unos 700 €.")],  # sin tool y con otra cifra: dos fallos
        ]
    )

    def crear():
        return Agente(llm=LLMFake(next(guiones)), tools=mundo.catalogo())

    bien, mal = evaluar(crear, [SEPT, SEPT], contexto())

    assert bien.aprobado and (bien.tools, bien.vueltas) == (("resumen_mes",), 2)
    assert not mal.aprobado
    salida = informe([bien, mal], con_ms=False)
    assert salida.splitlines()[:5] == [
        "✓ gasto-septiembre         2 vueltas ·    230 tokens · resumen_mes",
        "✗ gasto-septiembre         1 vueltas ·    120 tokens · sin tools",
        "    cifras: faltan 776,59",
        "    trayectoria: ninguna de ['resumen_mes']",
        "",
    ]
    assert "Aprobados 1 de 2 (50%)" in salida
    assert "Por grader: terminada 2/2 · cifras 1/2 · trayectoria 1/2" in salida


def test_si_el_modelo_falla_ese_caso_suspende_y_la_eval_sigue(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    guiones = iter(
        [
            [
                LLMNoDisponibleException(
                    "openai/gpt-oss-20b: 400 tool_use_failed Tool choice is none, but model called a tool"
                )
            ],
            [LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("Gastasteis 776,59 €.")],
        ]
    )
    caido, bien = evaluar(lambda: Agente(llm=LLMFake(next(guiones)), tools=mundo.catalogo()), [SEPT, SEPT], contexto())
    assert not caido.aprobado and caido.notas[0].detalle == "openai/gpt-oss-20b: 400 tool_use_failed"
    assert bien.aprobado


def test_el_juez_puntua_con_su_schema_y_sin_temperatura(mundo):
    llm = LLMFake([veredicto(5)])
    nota = JuezLLM(llm).juzgar(CON_RUBRICA, "En diciembre de 2025 no tenéis gastos.")
    assert (nota.ok, nota.detalle) == (True, "5/5: Cumple la rúbrica.")
    peticion = llm.peticiones[0]
    assert (peticion.esquema, peticion.temperatura, peticion.tools) == (ESQUEMA, 0, ())
    assert "<referencia>No hay.</referencia>" in peticion.mensajes[0].texto


def test_por_debajo_de_4_no_aprueba_y_sin_juez_tampoco():
    assert not JuezLLM(LLMFake([veredicto(2, "Inventa 120 €.")])).juzgar(CON_RUBRICA, "Gastasteis 120 €.").ok
    caido = JuezLLM(LLMFake([LLMNoDisponibleException("429")])).juzgar(CON_RUBRICA, "x")
    assert (caido.ok, caido.detalle) == (False, "sin veredicto (LLMNoDisponibleException)")
    fuera = JuezLLM(LLMFake([veredicto(7)])).juzgar(CON_RUBRICA, "x")  # fuera de la escala: no vale
    assert fuera.detalle == "sin veredicto (ValidationError)"


def test_un_caso_sin_rubrica_no_llama_al_juez():
    llm = LLMFake([])
    assert JuezLLM(llm).juzgar(SEPT, "x") is None and llm.peticiones == []


def test_la_puerta_del_ci_ve_los_casos_que_dejan_de_aprobar(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    resultados = evaluar(
        lambda: Agente(llm=LLMFake([LLMFake.responder("No lo sé.")]), tools=mundo.catalogo()), [SEPT], contexto()
    )
    assert regresiones(resultados, {"minimo": 1, "tienen_que_aprobar": ["gasto-septiembre"]}) == [
        "gasto-septiembre ya no aprueba",
        "0 aprobados, menos que el mínimo (1)",
    ]
    assert regresiones(resultados, {"minimo": 0, "tienen_que_aprobar": []}) == []
