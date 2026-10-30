"""Módulo 97: el adapter en streaming, sin red (un MockTransport que contesta Server-Sent Events con el formato de
Groq), y la reserva de modelos cuando ya ha salido texto."""

import json

import httpx2
import pytest
from openai import OpenAI

from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.pregunta_cancelada_exception import PreguntaCanceladaException
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.llm.llm_con_reserva import LLMConReserva
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM
from asistente.tests.fakes.llm_fake import LLMFake
from core.infrastructure.cache.circuit_breaker import CircuitBreaker

MODELO = "openai/gpt-oss-120b"
PETICION = PeticionLLM(sistema="Breve.", mensajes=(Mensaje.usuario("¿Cuánto?"),))


def trozo(delta: dict | None = None, fin: str | None = None, uso: dict | None = None) -> dict:
    eleccion = [] if delta is None else [{"index": 0, "delta": delta, "finish_reason": fin}]
    return {
        "id": "c1",
        "object": "chat.completion.chunk",
        "created": 1,
        "model": MODELO,
        "choices": eleccion,
        "usage": uso,
    }


def sse(*trozos) -> bytes:
    return "".join(f"data: {json.dumps(t)}\n\n" for t in trozos).encode() + b"data: [DONE]\n\n"


class Servidor:
    def __init__(self, *respuestas):
        self.respuestas, self.peticiones = list(respuestas), []

    def __call__(self, request):
        self.peticiones.append(json.loads(request.content))
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        if isinstance(r, tuple):
            return httpx2.Response(r[0], json=r[1])
        return httpx2.Response(200, content=r, headers={"content-type": "text/event-stream"})


def adapter(servidor) -> OpenAICompatibleLLM:
    cliente = OpenAI(
        base_url="https://groq.test/openai/v1",
        api_key="clave",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(servidor)),
    )
    return OpenAICompatibleLLM(cliente=cliente, modelo=MODELO, pausa=0)


USO = {
    "prompt_tokens": 120,
    "completion_tokens": 30,
    "total_tokens": 150,
    "completion_tokens_details": {"reasoning_tokens": 12},
}


def test_el_texto_sale_a_trozos_y_la_respuesta_es_la_de_siempre():
    servidor = Servidor(
        sse(
            trozo({"role": "assistant", "content": "", "reasoning": "Need"}),
            trozo({"content": "En septiembre "}),
            trozo({"content": "776,59 €."}),
            trozo({}, fin="stop"),
            trozo(uso=USO),
        )
    )
    trozos = []
    r = adapter(servidor).generar_en_streaming(PETICION, trozos.append)

    assert trozos == ["En septiembre ", "776,59 €."]
    assert (r.texto, r.motivo, r.razonamiento) == ("En septiembre 776,59 €.", MotivoFin.FIN, "Need")
    assert r.uso == Uso(entrada=120, salida=30, razonamiento=12)
    assert servidor.peticiones[0]["stream"] and servidor.peticiones[0]["stream_options"] == {"include_usage": True}


def test_las_tool_calls_llegan_en_trozos_y_se_juntan():
    servidor = Servidor(
        sse(
            trozo(
                {
                    "tool_calls": [
                        {
                            "index": 0,
                            "id": "fc_1",
                            "type": "function",
                            "function": {"name": "resumen_mes", "arguments": '{"mes":'},
                        }
                    ]
                }
            ),
            trozo({"tool_calls": [{"index": 0, "function": {"arguments": '"2026-09"}'}}]}),
            trozo({}, fin="tool_calls"),
            trozo(uso=USO),
        )
    )
    r = adapter(servidor).generar_en_streaming(PETICION, lambda t: None)
    assert (r.motivo, r.llamadas) == (MotivoFin.TOOLS, (LlamadaTool("fc_1", "resumen_mes", '{"mes":"2026-09"}'),))


def test_un_corte_antes_de_escribir_se_reintenta_y_despues_no():
    servidor = Servidor(httpx2.ConnectError("caído"), sse(trozo({"content": "Hola"}), trozo({}, fin="stop")))
    assert adapter(servidor).generar_en_streaming(PETICION, lambda t: None).texto == "Hola"

    class Corte(httpx2.SyncByteStream):  # un trozo de texto y la conexión se corta
        def __iter__(self):
            yield f"data: {json.dumps(trozo({'content': 'En sept'}))}\n\n".encode()
            raise httpx2.ReadError("cortado")

    cortado = httpx2.MockTransport(
        lambda r: httpx2.Response(200, stream=Corte(), headers={"content-type": "text/event-stream"})
    )
    cliente = OpenAI(
        base_url="https://groq.test/openai/v1", api_key="k", max_retries=0, http_client=httpx2.Client(transport=cortado)
    )
    trozos = []
    with pytest.raises(LLMNoDisponibleException):
        OpenAICompatibleLLM(cliente=cliente, modelo=MODELO, pausa=0).generar_en_streaming(PETICION, trozos.append)
    assert trozos == ["En sept"]  # una sola vez: lo ya enseñado no se repite con otro intento


def test_la_reserva_solo_si_no_ha_salido_nada():
    caido = LLMFake([LLMNoDisponibleException("429")], modelo="grande")
    reserva = LLMFake([LLMFake.responder("Hola desde el pequeño")], modelo="pequeño")
    llm = LLMConReserva([(caido, CircuitBreaker("llm:g1")), (reserva, CircuitBreaker("llm:p1"))])
    trozos = []
    assert llm.generar_en_streaming(PETICION, trozos.append).texto == "Hola desde el pequeño"
    assert trozos == ["Hola desde el pequeño"]


class EscribeYCae(LLMFake):
    def generar_en_streaming(self, peticion, al_texto):
        al_texto("En sept")
        raise LLMNoDisponibleException("cortado")


def test_a_mitad_de_respuesta_no_se_cambia_de_modelo():
    reserva = LLMFake([LLMFake.responder("otra")])
    llm = LLMConReserva([(EscribeYCae([]), CircuitBreaker("llm:g2")), (reserva, CircuitBreaker("llm:p2"))])
    with pytest.raises(LLMNoDisponibleException):
        llm.generar_en_streaming(PETICION, lambda t: None)
    assert reserva.peticiones == []


def test_cancelar_no_es_culpa_del_modelo():
    circuito = CircuitBreaker("llm:g3", umbral=1)
    llm = LLMConReserva([(LLMFake([LLMFake.responder("Hola")]), circuito), (LLMFake([]), CircuitBreaker("llm:p3"))])

    def cancelar(_):
        raise PreguntaCanceladaException()

    with pytest.raises(PreguntaCanceladaException):
        llm.generar_en_streaming(PETICION, cancelar)
    assert not circuito.abierto  # con umbral 1, un "fallo" lo habría abierto
