# asistente/infrastructure/telemetria/telemetria_otel.py — la pregunta y las tools, en spans y métricas (módulo 98)
"""El adapter de ITelemetriaDelAgente para OpenTelemetry. Una pregunta del chat se ve así en Tempo:

    POST …/preguntar/                              (Django, módulo 84)
    └── invoke_agent asistente                     gen_ai.agent.name, gen_ai.conversation.id, gastos.hogar.id
        ├── chat openai/gpt-oss-120b               (LLMMedido) modelo, tokens, finish_reasons, primer trozo, coste
        ├── execute_tool gasto_por_categoria       gen_ai.tool.name, gen_ai.tool.call.id
        │   └── SELECT …                           (psycopg, módulo 84)
        ├── chat openai/gpt-oss-120b
        └── chat openai/gpt-oss-120b               (la llamada que estructura la respuesta, módulo 96)

El hogar va en el span (las trazas se buscan una a una: un id más no cuesta) y NO en las métricas (cada valor de una
etiqueta es una serie temporal más en Prometheus: con miles de hogares, miles de series).
"""

import time
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

from asistente.application.agent.instrucciones import VERSION
from asistente.application.ports.i_telemetria_del_agente import ITelemetriaDelAgente
from asistente.domain.exceptions.pregunta_cancelada_exception import PreguntaCanceladaException
from asistente.infrastructure.telemetria import instrumentos

_trazador = trace.get_tracer("gastos.asistente")
AGENTE = "asistente"


class TelemetriaOTel(ITelemetriaDelAgente):
    @contextmanager
    def pregunta(self, contexto):
        atributos = {
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.agent.name": AGENTE,
            "gen_ai.prompt.name": "sistema",
            "gen_ai.prompt.version": VERSION,  # módulo 96: qué versión del prompt contestó
            "gastos.hogar.id": contexto.hogar.id,
        }
        if contexto.conversacion_id is not None:
            atributos["gen_ai.conversation.id"] = str(contexto.conversacion_id)
        with _trazador.start_as_current_span(
            f"invoke_agent {AGENTE}",
            kind=SpanKind.INTERNAL,
            attributes=atributos,
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            inicio = time.perf_counter()
            final = {"motivo": "error", "error": None}

            def medir(r) -> None:
                final["motivo"] = str(r.motivo)
                span.set_attributes(
                    {
                        "gen_ai.usage.input_tokens": r.uso.entrada,
                        "gen_ai.usage.output_tokens": r.uso.salida,
                        "gastos.asistente.motivo": str(r.motivo),
                        "gastos.asistente.vueltas": r.iteraciones,
                    }
                )
                version = {"gen_ai.prompt.version": VERSION}  # ejercicio 3
                instrumentos.vueltas.record(r.iteraciones, version)
                instrumentos.tokens_por_pregunta.record(r.uso.total, version)

            try:
                yield medir
            except PreguntaCanceladaException:  # la persona se ha ido: no es un error (ni rojo en Tempo ni alerta)
                final["motivo"] = "cancelada"
                span.set_attribute("gastos.asistente.motivo", "cancelada")
                raise
            except Exception as e:
                final["error"] = type(e).__name__
                span.set_attribute("error.type", final["error"])
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)[:200]))
                raise
            finally:
                duracion = {"gen_ai.agent.name": AGENTE}
                if final["error"]:
                    duracion["error.type"] = final["error"]
                instrumentos.duracion_agente.record(time.perf_counter() - inicio, duracion)
                instrumentos.preguntas.add(
                    1, {"gastos.asistente.motivo": final["motivo"], "gen_ai.prompt.version": VERSION}
                )

    @contextmanager
    def tool(self, llamada):
        atributos = {
            "gen_ai.operation.name": "execute_tool",
            "gen_ai.tool.name": llamada.nombre,
            "gen_ai.tool.call.id": llamada.id,
            "gen_ai.tool.type": "function",
        }
        with _trazador.start_as_current_span(
            f"execute_tool {llamada.nombre}", kind=SpanKind.INTERNAL, attributes=atributos
        ) as span:
            inicio = time.perf_counter()
            final = {"error": None}

            def medir(resultado) -> None:
                if resultado.es_error:  # el modelo recibe el error y se corrige; para quien opera, cuenta como error
                    final["error"] = "tool_error"
                    span.set_attribute("error.type", "tool_error")
                    span.set_status(Status(StatusCode.ERROR, "la tool ha devuelto un error al modelo"))

            try:
                yield medir
            finally:
                duracion = {"gen_ai.tool.name": llamada.nombre}
                if final["error"]:
                    duracion["error.type"] = final["error"]
                instrumentos.duracion_tool.record(time.perf_counter() - inicio, duracion)
