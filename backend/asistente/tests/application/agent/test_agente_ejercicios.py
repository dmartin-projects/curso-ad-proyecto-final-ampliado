"""Módulo 94, ejercicios 1 y 3: un presupuesto de tokens por pregunta y una línea de log por pregunta."""

import logging

from asistente.application.agent.limites import Limites
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.uso import Uso
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import contexto

PREGUNTA = (Mensaje.usuario("¿Cuánto gastamos?"),)


def caro(nombre, **args):
    r = LLMFake.llamar(nombre, **args)
    return r.__class__(r.mensaje, r.motivo, Uso(2500, 300), r.modelo)


def test_pasado_el_presupuesto_de_tokens_la_siguiente_vuelta_es_la_ultima(mundo):
    guion = [
        caro("resumen_mes", mes="2026-08"),
        caro("resumen_mes", mes="2026-09"),
        LLMFake.responder("Con lo que tengo…"),
    ]
    agente, llm = mundo.agente(guion, limites=Limites(max_tokens=5000))

    r = agente.responder(PREGUNTA, contexto())

    # 2.800 tras la primera vuelta (sigue), 5.600 tras la segunda (se pasa): la tercera, sin tools
    assert [p.usar_tools for p in llm.peticiones] == [True, True, False]
    assert (r.motivo, r.uso.total) == (MotivoParada.FIN, 5720)


def test_sin_presupuesto_no_hay_limite_de_tokens(mundo):
    agente, llm = mundo.agente([caro("resumen_mes"), LLMFake.responder("ok")])
    agente.responder(PREGUNTA, contexto())
    assert [p.usar_tools for p in llm.peticiones] == [True, True]


def test_una_linea_de_log_por_pregunta_sin_la_pregunta(mundo, caplog):
    agente, _ = mundo.agente([LLMFake.llamar("resumen_mes"), LLMFake.responder("812 €")])

    with caplog.at_level(logging.INFO, logger="asistente.application.agent.agente"):
        agente.responder(PREGUNTA, contexto())

    (registro,) = caplog.records
    assert registro.getMessage() == "Pregunta respondida: fin en 2 vueltas y 0 ms"
    assert registro.asistente == {
        "usuario_id": 7,
        "hogar_id": 3,
        "motivo": "fin",
        "iteraciones": 2,
        "tools": ["resumen_mes"],
        "modelos": ["fake"],
        "tokens_entrada": 200,
        "tokens_salida": 30,
        "tokens_razonamiento": 0,
        "tokens_cache": 0,
        "duracion_ms": 0,
    }
    assert "Cuánto" not in str(registro.__dict__)  # ni la pregunta ni la respuesta
