# estadisticas/infrastructure/telemetry/trazas_otel.py — ITrazas con OpenTelemetry: el span de cada mensaje
# (módulos 84, 85 y 89)
from collections.abc import Iterator
from contextlib import contextmanager

from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind

from estadisticas.application.ports.i_trazas import ITrazas
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO
from estadisticas.infrastructure.telemetry.traza_otel import TrazaOTel


class TrazasOTel(ITrazas):
    def __init__(self):
        self.tracer = trace.get_tracer("estadisticas.consumidor")

    @contextmanager
    def procesando(self, mensaje: MensajeInputDTO) -> Iterator[TrazaOTel]:
        # Este span cuelga del de publicación del relay, que cuelga de la petición que hizo el cambio
        with self.tracer.start_as_current_span(
            f"process {mensaje.topic}",
            context=propagate.extract(mensaje.cabeceras),
            kind=SpanKind.CONSUMER,
            attributes={
                "messaging.system": "kafka",
                "messaging.operation.type": "process",
                "messaging.destination.name": mensaje.topic,
                "messaging.destination.partition.id": str(mensaje.particion),
                "messaging.kafka.offset": mensaje.offset,
                "messaging.kafka.message.key": mensaje.clave,
            },
        ) as span:
            yield TrazaOTel(span)
