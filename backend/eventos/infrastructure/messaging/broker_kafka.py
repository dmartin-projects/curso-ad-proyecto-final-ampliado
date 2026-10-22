# eventos/infrastructure/messaging/broker_kafka.py — IBroker con un Producer de confluent-kafka (módulos 85 y 88)
import json

from opentelemetry import context, propagate, trace
from opentelemetry.trace import SpanKind

from eventos.application.ports.i_broker import IBroker
from eventos.domain.bo.evento_pendiente import EventoPendiente
from eventos.domain.exceptions.publicacion_no_confirmada_exception import PublicacionNoConfirmadaException
from eventos.domain.services.mensajes import ESQUEMA

tracer = trace.get_tracer("gastos.eventos")


def _cabeceras(p: EventoPendiente) -> list[tuple[str, str]]:
    cabeceras = {"tipo": p.mensaje.tipo, "version": str(p.id), "esquema": ESQUEMA}
    propagate.inject(cabeceras)  # traceparent del span de publicación en curso (ver BrokerKafka.publicar)
    return list(cabeceras.items())


class BrokerKafka(IBroker):
    """IBroker con un Producer de confluent-kafka (o cualquier objeto con produce/poll/flush: los tests)."""

    def __init__(self, productor, *, timeout: float = 30):
        self.productor, self.timeout = productor, timeout

    def publicar(self, lote: list[EventoPendiente]) -> None:
        errores: list = []

        def confirmado(error, mensaje):  # librdkafka la llama desde poll()/flush() con el resultado de cada envío
            if error is not None:
                errores.append(error)

        for p in lote:
            m = p.mensaje
            # La traza de quien hizo el cambio (guardada en el outbox) es la madre de este span: en Grafana,
            # petición → publicación (segundos después) → procesamiento en el otro servicio, todo en una traza.
            madre = propagate.extract({"traceparent": p.traceparent}) if p.traceparent else context.Context()
            with tracer.start_as_current_span(
                f"publish {m.topic}",
                context=madre,
                kind=SpanKind.PRODUCER,
                attributes={
                    "messaging.system": "kafka",
                    "messaging.operation.type": "publish",
                    "messaging.destination.name": m.topic,
                    "messaging.kafka.message.key": m.clave,
                    "gastos.evento.tipo": m.tipo,
                },
            ):
                valor = None if m.valor is None else json.dumps(m.valor, separators=(",", ":")).encode()
                self.productor.produce(
                    m.topic, key=m.clave.encode(), value=valor, headers=_cabeceras(p), on_delivery=confirmado
                )
            self.productor.poll(0)  # atiende confirmaciones ya llegadas sin bloquear

        sin_confirmar = self.productor.flush(self.timeout)  # espera a que Kafka confirme TODO el lote
        if sin_confirmar or errores:
            raise PublicacionNoConfirmadaException(
                f"{sin_confirmar} sin confirmar, {len(errores)} errores: {errores[:3]}"
            )
