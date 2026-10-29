"""Módulo 93: el adapter de Chat Completions sin red. Un MockTransport de httpx2 (el cliente HTTP del SDK de OpenAI)
contesta con el formato real de Groq; se comprueba la traducción en los dos sentidos y qué se reintenta."""

import json

import httpx2
import pytest
from openai import OpenAI

from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.peticion_llm_exception import PeticionLLMException
from asistente.domain.vo.declaracion_tool import DeclaracionTool
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.resultado_tool import ResultadoTool
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM

MODELO = "openai/gpt-oss-120b"
RESUMEN = DeclaracionTool(
    "resumen_mes", "Totales de un mes", {"type": "object", "properties": {"mes": {"type": "string"}}}
)


def completion(mensaje: dict, finish_reason="stop", usage=None) -> dict:
    """Una respuesta de Chat Completions con la forma que devuelve Groq (recortada)."""
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "created": 1793290819,
        "model": MODELO,
        "choices": [{"index": 0, "message": {"role": "assistant", **mensaje}, "finish_reason": finish_reason}],
        "usage": usage
        or {
            "prompt_tokens": 91,
            "completion_tokens": 39,
            "total_tokens": 130,
            "completion_tokens_details": {"reasoning_tokens": 9},
        },
    }


class Servidor:
    """Contesta, en orden, las respuestas que le den (un dict es un 200; una tupla, (status, cuerpo, cabeceras);
    una excepción de httpx2, un fallo de red) y guarda lo que le llega."""

    def __init__(self, *respuestas):
        self.respuestas, self.peticiones = list(respuestas), []

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        self.peticiones.append(json.loads(request.content))
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        status, cuerpo, cabeceras = r if isinstance(r, tuple) else (200, r, {})
        return httpx2.Response(status, json=cuerpo, headers=cabeceras)


def adapter(servidor: Servidor, intentos=2) -> OpenAICompatibleLLM:
    cliente = OpenAI(
        base_url="https://groq.test/openai/v1",
        api_key="clave-de-test",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(servidor)),
    )
    return OpenAICompatibleLLM(cliente=cliente, modelo=MODELO, intentos=intentos, pausa=0)


def peticion(**cambios) -> PeticionLLM:
    return PeticionLLM(**{"sistema": "Responde breve.", "mensajes": (Mensaje.usuario("¿Cuánto gastamos?"),)} | cambios)


def test_una_respuesta_de_texto():
    servidor = Servidor(completion({"content": "812,40 €.", "reasoning": "Need total."}))

    r = adapter(servidor).generar(peticion())

    assert (r.texto, r.motivo, r.modelo, r.razonamiento) == ("812,40 €.", MotivoFin.FIN, MODELO, "Need total.")
    assert r.uso == Uso(entrada=91, salida=39, razonamiento=9, cache=0)
    assert servidor.peticiones == [
        {
            "model": MODELO,
            "messages": [
                {"role": "system", "content": "Responde breve."},
                {"role": "user", "content": "¿Cuánto gastamos?"},
            ],
        }
    ]


def test_tool_calls_y_su_ida_y_vuelta():
    llamada = {"id": "fc_1", "type": "function", "function": {"name": "resumen_mes", "arguments": '{"mes":"2026-08"}'}}
    servidor = Servidor(completion({"content": None, "tool_calls": [llamada]}, finish_reason="tool_calls"))

    r = adapter(servidor).generar(peticion(tools=(RESUMEN,)))

    assert r.motivo == MotivoFin.TOOLS
    assert r.llamadas == (LlamadaTool("fc_1", "resumen_mes", '{"mes":"2026-08"}'),)
    enviado = servidor.peticiones[0]
    assert enviado["tools"] == [
        {
            "type": "function",
            "function": {"name": "resumen_mes", "description": "Totales de un mes", "parameters": RESUMEN.parametros},
        }
    ]
    assert enviado["tool_choice"] == "auto"

    # El siguiente turno: el del modelo, tal cual, y un mensaje "tool" por resultado, con el id de su llamada
    historial = (
        Mensaje.usuario("¿Cuánto gastamos?"),
        r.mensaje,
        Mensaje.de_tools((ResultadoTool("fc_1", "resumen_mes", '{"gastos": "812.40"}'),)),
    )
    servidor.respuestas.append(completion({"content": "812,40 €."}))
    adapter(servidor).generar(peticion(mensajes=historial, tools=(RESUMEN,), usar_tools=False))

    assert servidor.peticiones[1]["messages"][2:] == [
        {"role": "assistant", "content": None, "tool_calls": [llamada]},
        {"role": "tool", "tool_call_id": "fc_1", "content": '{"gastos": "812.40"}'},
    ]
    assert servidor.peticiones[1]["tool_choice"] == "none"  # la última vuelta: ve las tools, no puede llamarlas


def test_opciones_structured_output_y_cache():
    esquema = EsquemaRespuesta("movimiento", {"type": "object", "properties": {}, "additionalProperties": False})
    uso = {"prompt_tokens": 2000, "completion_tokens": 100, "prompt_tokens_details": {"cached_tokens": 1536}}
    servidor = Servidor(completion({"content": "{}"}, usage=uso))

    r = adapter(servidor).generar(
        peticion(esquema=esquema, temperatura=0.2, esfuerzo=EsfuerzoDeRazonamiento.ALTO, max_tokens=300)
    )

    enviado = servidor.peticiones[0]
    assert enviado["response_format"] == {
        "type": "json_schema",
        "json_schema": {"name": "movimiento", "schema": esquema.esquema, "strict": True},
    }
    assert (enviado["temperature"], enviado["reasoning_effort"], enviado["max_completion_tokens"]) == (0.2, "high", 300)
    assert r.uso == Uso(entrada=2000, salida=100, razonamiento=0, cache=1536)


@pytest.mark.parametrize(
    "finish_reason, motivo",
    [("length", MotivoFin.LIMITE_TOKENS), ("content_filter", MotivoFin.BLOQUEADA), ("raro", MotivoFin.OTRO)],
)
def test_motivos(finish_reason, motivo):
    servidor = Servidor(completion({"content": '{"conc'}, finish_reason=finish_reason))
    assert adapter(servidor).generar(peticion()).motivo == motivo


def test_un_5xx_se_reintenta():
    servidor = Servidor((503, {"error": {"message": "over capacity"}}, {}), completion({"content": "ok"}))

    assert adapter(servidor).generar(peticion()).texto == "ok"
    assert len(servidor.peticiones) == 2


def test_tras_los_intentos_un_5xx_es_transitorio():
    servidor = Servidor((503, {"error": {"message": "over capacity"}}, {}), (502, {}, {}))

    with pytest.raises(LLMNoDisponibleException, match="openai/gpt-oss-120b: 502"):
        adapter(servidor).generar(peticion())
    assert len(servidor.peticiones) == 2


def test_un_429_no_se_reintenta_y_dice_cuanto_esperar():
    error = {
        "error": {
            "message": "Rate limit reached for model `openai/gpt-oss-120b`",
            "type": "tokens",
            "code": "rate_limit_exceeded",
        }
    }
    servidor = Servidor((429, error, {"retry-after": "7"}))

    with pytest.raises(LLMNoDisponibleException, match="429 rate_limit_exceeded Rate limit reached") as e:
        adapter(servidor).generar(peticion())
    assert e.value.reintentar_en == 7.0
    assert len(servidor.peticiones) == 1


def test_un_fallo_de_red_se_reintenta_y_acaba_siendo_transitorio():
    servidor = Servidor(httpx2.ConnectError("sin red"), httpx2.ReadTimeout("lento"))

    with pytest.raises(LLMNoDisponibleException, match="APITimeoutError"):
        adapter(servidor).generar(peticion())
    assert len(servidor.peticiones) == 2


def test_una_tool_call_mal_formada_se_reintenta_aunque_sea_un_400():
    error = {
        "error": {
            "message": "Failed to call a function. Please adjust your prompt. See 'failed_generation' for more details.",
            "type": "invalid_request_error",
            "code": "tool_use_failed",
            "failed_generation": '{"name": "resumen_mes", "arguments": {"mes": 2026-09}}',
        }
    }
    servidor = Servidor((400, error, {}), (400, error, {}))

    with pytest.raises(LLMNoDisponibleException, match="400 tool_use_failed Failed to call a function"):
        adapter(servidor).generar(peticion(tools=(RESUMEN,)))
    assert len(servidor.peticiones) == 2


@pytest.mark.parametrize("status", [400, 401, 404, 413])
def test_un_4xx_es_culpa_de_la_peticion_y_no_se_reintenta(status):
    error = {
        "error": {
            "message": "The model `gpt-9` does not exist",
            "type": "invalid_request_error",
            "code": "model_not_found",
        }
    }
    servidor = Servidor((status, error, {}))

    with pytest.raises(PeticionLLMException, match=f"{status} model_not_found The model `gpt-9` does not exist"):
        adapter(servidor).generar(peticion())
    assert len(servidor.peticiones) == 1
