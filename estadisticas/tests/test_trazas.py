"""La traza cruza de Django al servicio por la cabecera `traceparent` del mensaje (módulos 84 y 85)."""

import json

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from estadisticas import consumidor, telemetria


class MensajeFalso:
    """Lo que devuelve Consumer.consume(): solo los métodos que usa procesar_lote()."""

    def __init__(self, cabeceras, offset=0):
        self._cabeceras = cabeceras
        self._offset = offset

    def error(self):
        return None

    def topic(self):
        return "gastos.movimientos"

    def partition(self):
        return 1

    def offset(self):
        return self._offset

    def key(self):
        return b"7"

    def value(self):
        return json.dumps({"id": 7, "hogar_id": 1, "cuenta_id": 1, "fecha": "2026-10-01", "importe": "-1.00",
                           "categoria_id": None, "comercio_id": None, "origen": "manual"}).encode()  # fmt: skip

    def headers(self):
        return [(k, v.encode()) for k, v in self._cabeceras.items()]

    def timestamp(self):
        return (1, 1_792_620_000_000)


@pytest.fixture(scope="module")
def spans():
    exportador = InMemorySpanExporter()
    assert telemetria.configurar("estadisticas-test", exportador=exportador)
    return exportador


def test_el_span_de_procesar_cuelga_del_de_publicar(spans):
    traza, padre = "4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7"
    cabeceras = {"version": "1", "esquema": "1", "traceparent": f"00-{traza}-{padre}-01"}
    consumidor.procesar_lote([MensajeFalso(cabeceras, offset=41)])
    [span] = [s for s in spans.get_finished_spans() if s.name == "process gastos.movimientos"]
    assert f"{span.context.trace_id:032x}" == traza  # la misma traza que la petición a Django
    assert f"{span.parent.span_id:016x}" == padre  # hija del span de publicación del relay
    assert span.attributes["messaging.kafka.offset"] == 41
    assert span.attributes["estadisticas.resultado"] == "guardado"
