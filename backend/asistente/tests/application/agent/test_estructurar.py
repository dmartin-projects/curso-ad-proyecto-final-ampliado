"""Módulo 96: la respuesta final en JSON, con una llamada más (sin tools y con el schema), validada aquí."""

import json

from asistente.application.agent.estructurar import ESQUEMA, MAX_SEGUIMIENTO, estructurar
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.read_models.respuesta_estructurada import Cifra, RespuestaEstructurada
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.uso import Uso
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import HOGAR, SEPTIEMBRE, contexto

CONVERSACION = (Mensaje.usuario("¿Cuánto gastamos en septiembre?"), Mensaje.modelo(texto="Gastasteis 812,40 €."))


def json_de(texto="Gastasteis 812,40 €.", cifras=(("Gasto de septiembre", "812,40 €"),), seguimiento=("¿Y agosto?",)):
    return json.dumps(
        {"texto": texto, "cifras": [{"concepto": c, "importe": i} for c, i in cifras], "seguimiento": list(seguimiento)}
    )


def test_la_respuesta_en_piezas_con_una_llamada_sin_tools():
    llm = LLMFake([LLMFake.responder(json_de())])
    forma, r = estructurar(llm, CONVERSACION)
    assert forma == RespuestaEstructurada(
        "Gastasteis 812,40 €.", (Cifra("Gasto de septiembre", "812,40 €"),), ("¿Y agosto?",)
    )
    peticion = llm.peticiones[0]
    assert (peticion.tools, peticion.esquema, peticion.mensajes) == ((), ESQUEMA, CONVERSACION)
    assert ESQUEMA.esquema["additionalProperties"] is False and ESQUEMA.estricto


def test_el_contenido_se_valida_aunque_la_forma_este_garantizada():
    preguntas = [f"¿Pregunta {n}?" for n in range(5)]
    forma, _ = estructurar(LLMFake([LLMFake.responder(json_de(seguimiento=preguntas))]), CONVERSACION)
    assert len(forma.seguimiento) == MAX_SEGUIMIENTO  # el schema no puede limitarlo en modo strict
    forma, r = estructurar(LLMFake([LLMFake.responder(json_de(cifras=(("", "1 €"),)))]), CONVERSACION)
    assert forma is None and r is not None  # un concepto vacío: sin forma, pero la llamada se pagó


def test_si_falla_la_pregunta_sigue_teniendo_su_texto(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="812.40")
    agente, llm = mundo.agente(
        [
            LLMFake.llamar("resumen_mes", mes="2026-09"),
            LLMFake.responder("Gastasteis 812,40 €."),
            LLMNoDisponibleException("sin cuota"),
        ]
    )
    r = agente.responder(CONVERSACION[:1], contexto(), estructurada=True)
    assert (r.texto, r.estructurada, r.iteraciones) == ("Gastasteis 812,40 €.", None, 2)


def test_el_agente_la_pide_al_final_y_la_suma_al_coste(mundo):
    agente, llm = mundo.agente(
        [LLMFake.responder("Gastasteis 812,40 €."), LLMFake.responder(json_de(), uso=Uso(300, 50))]
    )
    r = agente.responder(CONVERSACION[:1], contexto(), estructurada=True)
    assert r.estructurada.cifras == (Cifra("Gasto de septiembre", "812,40 €"),)
    assert (r.iteraciones, r.uso) == (2, Uso(400, 70))
    assert [m.texto for m in llm.peticiones[1].mensajes] == ["¿Cuánto gastamos en septiembre?", "Gastasteis 812,40 €."]
