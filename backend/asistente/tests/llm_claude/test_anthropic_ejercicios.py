"""Los ejercicios del 106: lo que cuesta escribir en la caché, contar los tokens antes de enviar y Claude de principal
con Groq de reserva a mitad de una pregunta."""

from decimal import Decimal

import httpx2
import pytest
from django.core.cache import cache

from asistente.application.agent.agente import Agente
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.precio import Precio
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.llm.llm_con_reserva import LLMConReserva
from asistente.infrastructure.tarifas.tarifas_desde_ajustes import TarifasDesdeAjustes
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.mundo import HOGAR, SEPTIEMBRE, Mundo, contexto
from asistente.tests.infrastructure.llm.test_openai_compatible_llm import Servidor, adapter, completion
from asistente.tests.llm_claude.respuestas import mensaje, tool_use
from asistente.tests.llm_claude.test_anthropic_llm import TOOL, Anthropic_
from core.infrastructure.cache.circuit_breaker import CircuitBreaker


def test_escribir_en_la_cache_cuesta_mas_que_leerla_y_que_la_entrada():
    """Ejercicio 1: la primera pregunta escribe el prefijo (1,25×), las siguientes lo leen (0,1×)."""
    haiku = TarifasDesdeAjustes().precio("claude-haiku-5-5")
    assert haiku == Precio(Decimal("0.10"), Decimal("0.50"), Decimal("0.01"), Decimal("0.125"))
    primera = Uso(entrada=3000, salida=100, cache_escrita=2800)
    siguiente = Uso(entrada=3000, salida=100, cache=2800)
    sin_cache = Uso(entrada=3000, salida=100)
    assert haiku.coste(primera) == Decimal("0.000420")  # 200 × 0,10 + 2.800 × 0,125 + 100 × 0,50, por millón
    assert haiku.coste(siguiente) == Decimal("0.000098")
    assert haiku.coste(sin_cache) == Decimal("0.000350")
    sin_precio_de_escritura = Precio(Decimal("0.15"), Decimal("0.60"), Decimal("0.075"))  # Groq: como la entrada
    assert sin_precio_de_escritura.coste(primera) == sin_precio_de_escritura.coste(sin_cache)


def test_el_uso_de_claude_separa_lo_escrito_en_la_cache():
    api = Anthropic_(mensaje([{"type": "text", "text": "Hola."}], "end_turn", entrada=50, salida=5, escritos=2900))
    r = api.llm().generar(PeticionLLM(sistema="x", mensajes=(Mensaje.usuario("y"),)))
    assert r.uso == Uso(entrada=2950, salida=5, cache_escrita=2900)


def test_contar_los_tokens_sin_generar_nada():
    """Ejercicio 2: /v1/messages/count_tokens, con lo que se mandaría (sin max_tokens ni la caché)."""
    api = Anthropic_({"input_tokens": 2817})
    p = PeticionLLM(sistema="Eres el asistente.", mensajes=(Mensaje.usuario("¿Septiembre?"),), tools=(TOOL,))
    assert api.llm().contar_tokens(p) == 2817
    (enviado,) = api.peticiones
    assert set(enviado) == {"model", "system", "messages", "tools", "tool_choice"}
    assert "cache_control" not in enviado["system"][0]


@pytest.fixture
def circuitos():
    cache.clear()  # el estado de los circuit breakers vive en la caché


@pytest.mark.usefixtures("circuitos")
def test_claude_cae_a_mitad_y_groq_sigue_la_misma_pregunta():
    """Ejercicio 3: Claude pide una tool (con su razonamiento firmado) y en la vuelta siguiente devuelve 529. La reserva
    (Groq) recibe el historial con la tool call y su resultado, sin el razonamiento de Claude (no es suyo), y contesta."""
    mundo = Mundo()
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    firmado = {"type": "thinking", "thinking": "", "signature": "EqQBCgIYAhIM"}
    claude = Anthropic_(
        mensaje([firmado, tool_use("resumen_mes", {"mes": "2026-09"})], "tool_use"),
        httpx2.Response(529, json={"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}),
    )
    groq = Servidor(completion({"content": "En septiembre gastasteis 776,59 €."}))
    llm = LLMConReserva(
        [
            (claude.llm(), CircuitBreaker("llm:claude", umbral=3, enfriamiento=120)),
            (adapter(groq), CircuitBreaker("llm:groq", umbral=3, enfriamiento=120)),
        ]
    )

    r = Agente(llm=llm, tools=mundo.tools()).responder((Mensaje.usuario("¿Septiembre?"),), contexto())

    assert (r.motivo, r.texto) == (MotivoParada.FIN, "En septiembre gastasteis 776,59 €.")
    assert r.modelos == ("claude-haiku-5-5", "openai/gpt-oss-120b")
    usuario, asistente, herramienta = groq.peticiones[0]["messages"][1:]
    assert asistente["tool_calls"][0]["function"]["name"] == "resumen_mes"
    assert "signature" not in str(asistente)
    assert herramienta["role"] == "tool" and "776.59" in herramienta["content"]
