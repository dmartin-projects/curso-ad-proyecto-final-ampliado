"""Módulo 106: el adapter de Claude, con el SDK oficial y un transporte HTTP falso que contesta como la Messages API
documentada: la traducción de ida (cuerpo) y de vuelta (respuesta, uso, errores) y el agent loop de verdad encima."""

import json

import httpx2
import pytest
from anthropic import Anthropic

from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.peticion_llm_exception import PeticionLLMException
from asistente.domain.vo.declaracion_tool import DeclaracionTool
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.resultado_tool import ResultadoTool
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.llm.anthropic_llm import AnthropicLLM, cuerpo
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.mundo import HOGAR, SEPTIEMBRE, Mundo, contexto
from asistente.tests.llm_claude.respuestas import mensaje, stream_de_texto, texto, tool_use

TOOL = DeclaracionTool("resumen_mes", "El resumen de un mes.", {"type": "object", "properties": {}})


class Anthropic_:
    """Un cliente del SDK oficial con un transporte que contesta lo que el test quiere y apunta lo que recibe."""

    def __init__(self, *respuestas):
        self.respuestas, self.peticiones = list(respuestas), []
        transporte = httpx2.MockTransport(self._contestar)
        self.cliente = Anthropic(api_key="sin-clave", http_client=httpx2.Client(transport=transporte), max_retries=0)

    def _contestar(self, peticion: httpx2.Request) -> httpx2.Response:
        self.peticiones.append(json.loads(peticion.content))
        r = self.respuestas.pop(0)
        if isinstance(r, httpx2.Response):
            return r
        if isinstance(r, bytes):
            return httpx2.Response(200, content=r, headers={"content-type": "text/event-stream"})
        return httpx2.Response(200, json=r)

    def llm(self) -> AnthropicLLM:
        return AnthropicLLM(cliente=self.cliente, modelo="claude-haiku-5-5")


def test_el_cuerpo_de_la_messages_api():
    p = PeticionLLM(
        sistema="Eres el asistente de Gastos.",
        mensajes=(
            Mensaje.usuario("¿Cuánto en septiembre?"),
            Mensaje.modelo(llamadas=(LlamadaTool("toolu_1", "resumen_mes", '{"mes":"2026-09"}'),
                                     LlamadaTool("toolu_2", "resumen_mes", "{roto"))),
            Mensaje.de_tools((ResultadoTool("toolu_1", "resumen_mes", '{"gastos":"776.59"}'),
                              ResultadoTool("toolu_2", "resumen_mes", '{"error":"…"}', es_error=True))),
        ),
        tools=(TOOL,),
        usar_tools=False,
        esquema=EsquemaRespuesta("respuesta", {"type": "object"}),
        esfuerzo=EsfuerzoDeRazonamiento.BAJO,
        temperatura=1.5,
    )  # fmt: skip
    c = cuerpo("claude-haiku-5-5", p)
    assert c["system"] == [
        {"type": "text", "text": "Eres el asistente de Gastos.", "cache_control": {"type": "ephemeral"}}
    ]
    assert c["cache_control"] == {"type": "ephemeral"}  # la caché automática, que avanza con la conversación
    assert c["tools"] == [
        {"name": "resumen_mes", "description": "El resumen de un mes.", "input_schema": TOOL.parametros}
    ]
    assert c["tool_choice"] == {"type": "none"}  # la última vuelta: ve las tools, no las pide
    assert c["output_config"] == {"format": {"type": "json_schema", "schema": {"type": "object"}}, "effort": "low"}
    assert (c["temperature"], c["max_tokens"]) == (1.0, 4096)
    usuario, asistente, resultados = c["messages"]
    assert asistente["content"] == [
        {"type": "tool_use", "id": "toolu_1", "name": "resumen_mes", "input": {"mes": "2026-09"}},
        {"type": "tool_use", "id": "toolu_2", "name": "resumen_mes", "input": {}},  # el roto, vacío
    ]
    assert resultados == {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_1", "content": '{"gastos":"776.59"}'},
        {"type": "tool_result", "tool_use_id": "toolu_2", "content": '{"error":"…"}', "is_error": True},
    ]}  # fmt: skip


def test_sin_cache_ni_un_cache_control():
    c = cuerpo("claude-haiku-5-5", PeticionLLM(sistema="x", mensajes=(Mensaje.usuario("y"),)), cache=False)
    assert "cache_control" not in c and "cache_control" not in c["system"][0]


def test_la_respuesta_tool_use_y_el_uso_con_cache():
    api = Anthropic_(mensaje([texto("Voy a mirarlo."), tool_use("resumen_mes", {"mes": "2026-09"})], "tool_use",
                             entrada=40, salida=60, leidos=2800, escritos=0))  # fmt: skip
    r = api.llm().generar(PeticionLLM(sistema="x", mensajes=(Mensaje.usuario("¿Septiembre?"),), tools=(TOOL,)))
    assert r.motivo == MotivoFin.TOOLS
    assert r.llamadas == (LlamadaTool("toolu_01A09q90qw90lq917835lq9", "resumen_mes", '{"mes": "2026-09"}'),)
    assert r.texto == "Voy a mirarlo."
    assert r.uso == Uso(entrada=2840, salida=60, cache=2800)  # entrada total = sin caché + leídos + escritos


@pytest.mark.parametrize(
    ("stop", "motivo"),
    [("end_turn", MotivoFin.FIN), ("max_tokens", MotivoFin.LIMITE_TOKENS), ("refusal", MotivoFin.BLOQUEADA),
     ("model_context_window_exceeded", MotivoFin.LIMITE_TOKENS)],
)  # fmt: skip
def test_los_stop_reason(stop, motivo):
    r = (
        Anthropic_(mensaje([texto("…")], stop))
        .llm()
        .generar(PeticionLLM(sistema="x", mensajes=(Mensaje.usuario("y"),)))
    )
    assert r.motivo == motivo


def test_los_errores_del_sdk_traducidos():
    p = PeticionLLM(sistema="x", mensajes=(Mensaje.usuario("y"),))
    error = {"type": "error", "error": {"type": "rate_limit_error", "message": "Number of request tokens has exceeded"}}
    con_espera = Anthropic_(httpx2.Response(429, json=error, headers={"retry-after": "7"})).llm()
    with pytest.raises(LLMNoDisponibleException) as e:
        con_espera.generar(p)
    assert e.value.reintentar_en == 7.0
    with pytest.raises(LLMNoDisponibleException):  # 529: overloaded
        Anthropic_(httpx2.Response(529, json={"type": "error", "error": {"type": "overloaded_error"}})).llm().generar(p)
    with pytest.raises(PeticionLLMException):
        Anthropic_(
            httpx2.Response(400, json={"type": "error", "error": {"type": "invalid_request_error"}})
        ).llm().generar(p)


def test_en_streaming_el_texto_sale_a_trozos():
    trozos = []
    r = (
        Anthropic_(stream_de_texto(["En septiembre ", "gastasteis ", "776,59 €."]))
        .llm()
        .generar_en_streaming(PeticionLLM(sistema="x", mensajes=(Mensaje.usuario("y"),)), trozos.append)
    )
    assert trozos == ["En septiembre ", "gastasteis ", "776,59 €."]
    assert (r.texto, r.motivo) == ("En septiembre gastasteis 776,59 €.", MotivoFin.FIN)


def test_el_agent_loop_con_claude_sin_cambiar_nada():
    mundo = Mundo()
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    api = Anthropic_(
        mensaje([tool_use("resumen_mes", {"mes": "2026-09"})], "tool_use"),
        mensaje([texto("En septiembre gastasteis 776,59 €.")], "end_turn"),
    )
    from asistente.application.agent.agente import Agente

    r = Agente(llm=api.llm(), tools=mundo.tools()).responder((Mensaje.usuario("¿Septiembre?"),), contexto())

    assert (r.texto, r.motivo, r.iteraciones) == ("En septiembre gastasteis 776,59 €.", MotivoParada.FIN, 2)
    segunda = api.peticiones[1]["messages"]
    assert segunda[1]["content"][0]["type"] == "tool_use"
    assert segunda[2]["content"][0]["tool_use_id"] == "toolu_01A09q90qw90lq917835lq9"
    assert json.loads(segunda[2]["content"][0]["content"])["gastos"] == "776.59"


def test_la_clave_de_anthropic_no_se_graba_en_los_cassettes():
    from asistente.tests.conftest import vcr_config

    assert "x-api-key" in vcr_config.__wrapped__()["filter_headers"]  # Anthropic no usa Authorization


def test_el_razonamiento_firmado_vuelve_entero_con_su_tool_use():
    """Claude 5.5 razona por defecto y, sin pedirlo, sin texto (display "omitted"): llega un bloque `thinking` vacío con
    su firma. En un turno con tools, hay que devolverlo tal cual, antes del tool_use."""
    mundo = Mundo()
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    pensado = {"type": "thinking", "thinking": "", "signature": "EqQBCgIYAhIM1gbcDa9GJwZA2b3hGgxBdjrkzLoky3dl1pk"}
    api = Anthropic_(
        mensaje([pensado, tool_use("resumen_mes", {"mes": "2026-09"})], "tool_use"),
        mensaje([texto("En septiembre gastasteis 776,59 €.")], "end_turn"),
    )
    from asistente.application.agent.agente import Agente

    r = Agente(llm=api.llm(), tools=mundo.tools()).responder((Mensaje.usuario("¿Septiembre?"),), contexto())

    assert r.motivo == MotivoParada.FIN
    asistente = api.peticiones[1]["messages"][1]
    assert asistente["content"][0] == pensado  # primero, y sin tocar una coma
    assert asistente["content"][1]["type"] == "tool_use"
