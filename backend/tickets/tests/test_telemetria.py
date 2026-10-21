"""Módulo 84: la traza de un ticket, de la subida al gasto, y su métrica de negocio."""

import pytest
from opentelemetry import trace
from opentelemetry.trace import SpanKind

from .conftest import URL_IA, datos_ia, respuesta_ia
from .test_api import escenario, subir  # noqa: F401 (fixtures)

pytestmark = pytest.mark.django_db
PROCESADOS = "gastos.tickets.procesados"


def test_subir_un_ticket_es_una_sola_traza_de_punta_a_punta(telemetria, escenario, subir, respx_mock):  # noqa: F811
    hogar, roles, cuenta, _ = escenario
    respx_mock.post(URL_IA).mock(return_value=respuesta_ia(datos_ia()))
    antes = telemetria.metrica(PROCESADOS).get((("estado", "procesado"),), 0)

    # En el test, los on_commit (el .delay()) se ejecutan al salir de django_capture_on_commit_callbacks,
    # DESPUÉS de la petición. En producción se ejecutan dentro de ella, al confirmar la transacción.
    # Un span alrededor hace de "petición" para que la tarea cuelgue de la misma traza, como en producción.
    with trace.get_tracer("pruebas").start_as_current_span("peticion") as raiz:
        r = subir(hogar, roles["miembro"], cuenta)
    assert r.status_code == 202
    traza = raiz.get_span_context().trace_id

    # (dentro de otro span, Django marca el suyo como INTERNAL en vez de SERVER; y en modo eager Celery no
    # publica nada, así que no hay span de "encolar": el recorrido real por RabbitMQ se ve en Tempo: §7 del módulo)
    [servidor] = [s for s in telemetria.spans() if s.name.startswith("POST api/")]
    [tarea] = telemetria.spans("run/tickets.tasks.procesar_ticket")
    [ocr] = telemetria.spans("ticket.ocr")
    [ia] = telemetria.spans("ticket.ia")
    [llamada] = [s for s in telemetria.spans() if s.kind == SpanKind.CLIENT and s.name == "POST"]
    assert {s.context.trace_id for s in (servidor, tarea, ocr, ia, llamada)} == {traza}
    assert tarea.kind == SpanKind.CONSUMER
    assert ocr.parent.span_id == ia.parent.span_id == tarea.context.span_id  # los dos pasos, dentro de la tarea
    assert llamada.parent.span_id == ia.context.span_id  # la llamada HTTP a la IA, dentro de ticket.ia
    # atributos útiles para filtrar en Tempo, nunca el contenido del ticket
    assert ocr.attributes["ocr.caracteres"] > 0 and ocr.attributes["ocr.util"] is True
    assert ia.attributes["ia.confianza"] == 0.93
    assert "Mercadona" not in repr([dict(s.attributes) for s in telemetria.spans()])

    assert telemetria.metrica(PROCESADOS)[(("estado", "procesado"),)] == antes + 1
