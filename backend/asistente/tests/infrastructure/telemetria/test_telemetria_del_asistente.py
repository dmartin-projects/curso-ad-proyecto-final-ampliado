"""Módulo 98: una pregunta en spans y métricas con las convenciones GenAI de OpenTelemetry. El agente de verdad, con
LLMFake detrás de LLMMedido y las tools del mundo de fakes; la telemetría, en memoria (el fixture `telemetria`)."""

from dataclasses import replace
from decimal import Decimal

import pytest
from opentelemetry.trace import SpanKind, StatusCode

from asistente.application.agent.agente import Agente
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.pregunta_cancelada_exception import PreguntaCanceladaException
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.precio import Precio
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.telemetria.llm_medido import LLMMedido
from asistente.infrastructure.telemetria.telemetria_otel import TelemetriaOTel
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import Mundo, contexto

M = "openai/gpt-oss-120b"
PRECIO = Precio(Decimal("0.15"), Decimal("0.60"), Decimal("0.075"))


def medido(guion) -> tuple[LLMMedido, LLMFake]:
    fake = LLMFake(guion, modelo=M)
    return LLMMedido(fake, proveedor="groq", base_url="https://api.groq.com/openai/v1", precio=lambda m: PRECIO), fake


def agente(guion) -> Agente:
    llm, _ = medido(guion)
    return Agente(llm=llm, tools=Mundo().tools(), telemetria=TelemetriaOTel())


def test_una_pregunta_es_un_arbol_de_spans(telemetria):
    a = agente(
        [
            LLMFake.llamar("gasto_por_categoria", mes="2026-09"),
            LLMFake.responder("776,59 €", Uso(1200, 80, razonamiento=30, cache=1024), modelo=M),
        ]
    )
    a.responder((Mensaje.usuario("¿Septiembre?"),), replace(contexto(), conversacion_id=12))

    [pregunta] = telemetria.spans("invoke_agent asistente")
    chats = telemetria.spans(f"chat {M}")
    [tool] = telemetria.spans("execute_tool gasto_por_categoria")
    assert len(chats) == 2
    assert all(s.parent.span_id == pregunta.context.span_id for s in [*chats, tool])  # todo cuelga de la pregunta
    assert pregunta.attributes["gen_ai.conversation.id"] == "12" and pregunta.attributes["gastos.hogar.id"] == 3
    assert (
        pregunta.attributes["gastos.asistente.motivo"] == "fin" and pregunta.attributes["gastos.asistente.vueltas"] == 2
    )
    assert pregunta.attributes["gen_ai.usage.input_tokens"] == 1300  # 100 de la vuelta de la tool + 1200

    ultimo = chats[1]
    assert ultimo.kind == SpanKind.CLIENT
    assert {k: ultimo.attributes[k] for k in ultimo.attributes if k.startswith(("gen_ai.", "server."))} == {
        "gen_ai.operation.name": "chat",
        "gen_ai.provider.name": "groq",
        "gen_ai.request.model": M,
        "gen_ai.request.stream": False,
        "gen_ai.output.type": "text",
        "server.address": "api.groq.com",
        "gen_ai.response.model": M,
        "gen_ai.response.finish_reasons": ("stop",),
        "gen_ai.usage.input_tokens": 1200,
        "gen_ai.usage.output_tokens": 80,
        "gen_ai.usage.cache_read.input_tokens": 1024,
        "gen_ai.usage.reasoning.output_tokens": 30,
    }
    # (1200 − 1024) × 0,15 + 1024 × 0,075 + 80 × 0,60, por millón
    assert ultimo.attributes["gastos.asistente.coste_usd"] == pytest.approx(0.000151)
    assert (tool.attributes["gen_ai.tool.call.id"], tool.attributes["gen_ai.tool.type"]) == ("fake-0", "function")


def test_nada_del_texto_viaja_en_los_spans(telemetria):
    agente([LLMFake.responder("Un secreto del hogar")]).responder((Mensaje.usuario("mi nómina"),), contexto())
    for s in telemetria.spans():
        assert not any("secreto" in str(v) or "nómina" in str(v) for v in s.attributes.values())


def test_tokens_y_coste_en_las_metricas_por_modelo_sin_hogar(telemetria):
    clave = (("gen_ai.operation.name", "chat"), ("gen_ai.provider.name", "groq"), ("gen_ai.request.model", M),
             ("gen_ai.response.model", M), ("gen_ai.token.modality", "text"), ("server.address", "api.groq.com"))  # fmt: skip
    antes = telemetria.metrica("gen_ai.client.inference.usage.input_tokens").get(clave, 0)
    coste_antes = sum(telemetria.metrica("gastos.asistente.coste_usd").values())
    agente([LLMFake.responder("Hola", Uso(2000, 100), modelo=M)]).responder((Mensaje.usuario("Hola"),), contexto())

    assert telemetria.metrica("gen_ai.client.inference.usage.input_tokens")[clave] == antes + 2000
    assert sum(telemetria.metrica("gastos.asistente.coste_usd").values()) == pytest.approx(coste_antes + 0.00036)
    for nombre in ("gen_ai.client.inference.usage.input_tokens", "gastos.asistente.coste_usd"):
        assert all("gastos.hogar.id" not in dict(k) for k in telemetria.metrica(nombre))  # cardinalidad


def test_un_error_del_modelo_queda_en_rojo_con_su_tipo(telemetria):
    llm, _ = medido([LLMNoDisponibleException("429 rate_limit_exceeded", 30.0)])
    with pytest.raises(LLMNoDisponibleException):
        Agente(llm=llm, tools=[], telemetria=TelemetriaOTel()).responder((Mensaje.usuario("Hola"),), contexto())
    [chat] = telemetria.spans(f"chat {M}")
    [pregunta] = telemetria.spans("invoke_agent asistente")
    assert chat.status.status_code == StatusCode.ERROR and chat.attributes["error.type"] == "LLMNoDisponibleException"
    assert pregunta.status.status_code == StatusCode.ERROR


def test_cancelar_no_es_un_error(telemetria):
    def se_va(_trozo):
        raise PreguntaCanceladaException()

    llm, _ = medido([LLMFake.responder("Esto no lo lee nadie")])
    with pytest.raises(PreguntaCanceladaException):
        Agente(llm=llm, tools=[], telemetria=TelemetriaOTel()).responder(
            (Mensaje.usuario("Hola"),), contexto(), al_texto=se_va
        )
    [chat] = telemetria.spans(f"chat {M}")
    [pregunta] = telemetria.spans("invoke_agent asistente")
    assert chat.status.status_code == StatusCode.UNSET and chat.attributes["error.type"] == "cancelada"
    assert pregunta.status.status_code == StatusCode.UNSET
    assert pregunta.attributes["gastos.asistente.motivo"] == "cancelada"


def test_una_tool_que_falla_cuenta_como_error_de_esa_tool(telemetria):
    agente(
        [LLMFake.llamar("gasto_por_categoria", mes="no-es-un-mes"), LLMFake.responder("Perdón", modelo=M)]
    ).responder((Mensaje.usuario("¿?"),), contexto())
    [tool] = telemetria.spans("execute_tool gasto_por_categoria")
    assert tool.attributes["error.type"] == "tool_error" and tool.status.status_code == StatusCode.ERROR
    errores = telemetria.metrica("gen_ai.execute_tool.duration")
    assert (("error.type", "tool_error"), ("gen_ai.tool.name", "gasto_por_categoria")) in errores


def test_el_primer_trozo_en_streaming(telemetria):
    llm, _ = medido([LLMFake.responder("Hola", modelo=M)])
    llm.generar_en_streaming(PeticionLLM(sistema="", mensajes=(Mensaje.usuario("Hola"),)), lambda trozo: None)
    [chat] = telemetria.spans(f"chat {M}")
    assert chat.attributes["gen_ai.request.stream"] is True
    assert chat.attributes["gen_ai.response.time_to_first_chunk"] >= 0
