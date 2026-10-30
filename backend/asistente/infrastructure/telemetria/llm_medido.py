# asistente/infrastructure/telemetria/llm_medido.py — cada llamada al modelo, con su span y sus métricas (módulo 98)
"""Un decorator del port ILLM (como LLMConReserva): envuelve UN modelo y mide cada llamada con las convenciones GenAI.

    LLMConReserva([(LLMMedido(OpenAICompatibleLLM(…120b…)), …), (LLMMedido(OpenAICompatibleLLM(…20b…)), …)])

Dentro de la reserva y no fuera: si el principal da un 429 y contesta el de reserva, son DOS spans (uno con el error,
otro con la respuesta), cada uno con su modelo. Por fuera se vería una sola llamada lenta.

Lo que nunca va al span: el prompt y la respuesta (los atributos gen_ai.input.messages y gen_ai.output.messages son
opt-in en la especificación, y aquí siguen apagados). Son datos del hogar: las trazas los guardarían semanas en un
sistema que no se diseñó para guardarlos (módulo 107).
"""

import time
from collections.abc import Callable
from urllib.parse import urlparse

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

from asistente.application.ports.i_llm import ILLM
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.precio import Precio
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.infrastructure.telemetria import instrumentos

_trazador = trace.get_tracer("gastos.asistente")

# gen_ai.response.finish_reasons: los valores del proveedor (los de Chat Completions), no los nuestros
FINISH_REASONS = {
    MotivoFin.FIN: "stop",
    MotivoFin.TOOLS: "tool_calls",
    MotivoFin.LIMITE_TOKENS: "length",
    MotivoFin.BLOQUEADA: "content_filter",
    MotivoFin.OTRO: "other",
}


class LLMMedido(ILLM):
    def __init__(self, dentro: ILLM, *, proveedor: str, base_url: str, precio: Callable[[str], Precio | None]):
        self.dentro = dentro
        self.proveedor = proveedor  # gen_ai.provider.name: "groq" (un valor conocido de la especificación)
        self.servidor = urlparse(base_url).hostname or ""
        self.precio = precio

    @property
    def modelo(self) -> str:
        return self.dentro.modelo

    def generar(self, peticion: PeticionLLM) -> RespuestaLLM:
        return self._medir(peticion, False, lambda _: self.dentro.generar(peticion))

    def generar_en_streaming(self, peticion: PeticionLLM, al_texto: Callable[[str], None]) -> RespuestaLLM:
        return self._medir(peticion, True, lambda medir: self.dentro.generar_en_streaming(peticion, medir(al_texto)))

    def _medir(self, peticion: PeticionLLM, stream: bool, llamar) -> RespuestaLLM:
        base = {
            "gen_ai.operation.name": "chat",
            "gen_ai.provider.name": self.proveedor,
            "gen_ai.request.model": self.modelo,
            "server.address": self.servidor,
        }
        atributos = {
            **base,
            "gen_ai.request.stream": stream,
            "gen_ai.output.type": "json" if peticion.esquema else "text",
        }
        if peticion.max_tokens is not None:
            atributos["gen_ai.request.max_tokens"] = peticion.max_tokens
        if peticion.temperatura is not None:
            atributos["gen_ai.request.temperature"] = peticion.temperatura
        # El nombre, como dice la especificación: "{operación} {modelo}". Kind CLIENT: el modelo está en otro proceso
        with _trazador.start_as_current_span(
            f"chat {self.modelo}",
            kind=SpanKind.CLIENT,
            attributes=atributos,
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            inicio = time.perf_counter()
            estado = {"primer": None, "interrumpido": False}

            def medir(al_texto: Callable[[str], None]) -> Callable[[str], None]:
                def envuelto(trozo: str) -> None:
                    if estado["primer"] is None:
                        estado["primer"] = time.perf_counter()
                    try:
                        al_texto(trozo)
                    except BaseException:
                        estado["interrumpido"] = True  # lo ha cortado quien escucha (una cancelación): no es un fallo
                        raise

                return envuelto

            try:
                r = llamar(medir)
            except Exception as e:
                tipo = "cancelada" if estado["interrumpido"] else type(e).__name__
                span.set_attribute("error.type", tipo)
                if not estado["interrumpido"]:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)[:200]))
                instrumentos.duracion_inferencia.record(time.perf_counter() - inicio, base | {"error.type": tipo})
                raise
            duracion = time.perf_counter() - inicio
            con_respuesta = base | {"gen_ai.response.model": r.modelo}
            span.set_attributes(
                {
                    "gen_ai.response.model": r.modelo,
                    "gen_ai.response.finish_reasons": [FINISH_REASONS[r.motivo]],
                    "gen_ai.usage.input_tokens": r.uso.entrada,
                    "gen_ai.usage.output_tokens": r.uso.salida,
                    "gen_ai.usage.cache_read.input_tokens": r.uso.cache,
                    "gen_ai.usage.reasoning.output_tokens": r.uso.razonamiento,
                }
            )
            instrumentos.duracion_inferencia.record(duracion, con_respuesta)
            if estado["primer"] is not None:
                ttft = estado["primer"] - inicio
                span.set_attribute("gen_ai.response.time_to_first_chunk", ttft)
                instrumentos.primer_trozo.record(ttft, con_respuesta)
            texto = con_respuesta | {"gen_ai.token.modality": "text"}  # Groq no lo desglosa: todo es texto aquí
            instrumentos.tokens_entrada.add(r.uso.entrada, texto)
            instrumentos.tokens_salida.add(r.uso.salida, texto)
            instrumentos.tokens_cache.add(r.uso.cache, texto)
            instrumentos.tokens_razonamiento.add(r.uso.razonamiento, texto)
            if (precio := self.precio(r.modelo)) is not None:
                coste = float(precio.coste(r.uso))
                span.set_attribute("gastos.asistente.coste_usd", coste)
                instrumentos.coste.add(
                    coste, {"gen_ai.provider.name": self.proveedor, "gen_ai.response.model": r.modelo}
                )
            return r
