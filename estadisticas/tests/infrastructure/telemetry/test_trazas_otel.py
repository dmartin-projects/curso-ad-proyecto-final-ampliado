"""La traza cruza de Django al servicio por la cabecera `traceparent` del mensaje (módulos 84, 85 y 89).

Se prueba el adapter de OpenTelemetry (TrazasOTel) con el use case de verdad y los demás ports en memoria:
para esto no hacen falta ni Kafka ni PostgreSQL.
"""

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from estadisticas.infrastructure.telemetry import telemetria
from estadisticas.infrastructure.telemetry.trazas_otel import TrazasOTel
from tests.fakes.mundo import Mundo, lote, movimiento


@pytest.fixture(scope="module")
def spans():
    exportador = InMemorySpanExporter()
    assert telemetria.configurar("estadisticas-test", exportador=exportador)
    return exportador


def test_el_span_de_procesar_cuelga_del_de_publicar(spans):
    traza, padre = "4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7"
    mundo = Mundo()
    mensaje = movimiento(7, offset=41, traceparent=f"00-{traza}-{padre}-01")
    mundo.procesar_lote(trazas=TrazasOTel()).ejecutar(lote([mensaje]))
    [span] = [s for s in spans.get_finished_spans() if s.name == "process gastos.movimientos"]
    assert f"{span.context.trace_id:032x}" == traza  # la misma traza que la petición a Django
    assert f"{span.parent.span_id:016x}" == padre  # hija del span de publicación del relay
    assert span.attributes["messaging.kafka.offset"] == 41
    assert span.attributes["messaging.kafka.message.key"] == "7"
    assert span.attributes["estadisticas.resultado"] == "guardado"
