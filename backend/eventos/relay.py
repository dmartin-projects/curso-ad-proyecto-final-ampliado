"""El relay del outbox (módulo 85): lee los eventos pendientes de PostgreSQL y los publica en Kafka.

Garantía: AL MENOS UNA VEZ. Un evento se marca como publicado solo después de que Kafka lo confirme; si
el proceso muere entre la confirmación y el UPDATE, al volver lo publica otra vez. Los consumidores tienen
que ser idempotentes (el servicio de estadísticas lo es: se queda con la versión más alta de cada objeto).
"""

import json
import logging

from django.db import transaction
from django.utils import timezone
from opentelemetry import context, metrics, propagate, trace
from opentelemetry.instrumentation.utils import suppress_instrumentation
from opentelemetry.trace import SpanKind

from .models import EventoPendiente
from .topics import ESQUEMA

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("gastos.eventos")
medidor = metrics.get_meter("gastos.eventos")
publicados = medidor.create_counter(
    "gastos.eventos.publicados", unit="{evento}", description="Eventos publicados en Kafka"
)
retraso = medidor.create_histogram(
    "gastos.eventos.retraso",
    unit="s",
    description="Tiempo desde que se guarda el evento hasta que Kafka lo confirma",
    explicit_bucket_boundaries_advisory=[0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 300],
)


class ErrorDePublicacion(Exception):
    """Kafka no ha confirmado todo el lote: no se marca nada y se reintentará."""


def _cabeceras(ev: EventoPendiente) -> list[tuple[str, str]]:
    cabeceras = {"tipo": ev.tipo, "version": str(ev.pk), "esquema": ESQUEMA}
    propagate.inject(cabeceras)  # traceparent del span de publicación en curso (ver publicar_lote)
    return list(cabeceras.items())


def publicar_lote(productor, *, tamano: int = 500, timeout: float = 30) -> int:
    """Publica hasta `tamano` eventos pendientes, en orden de id. Devuelve cuántos ha publicado."""
    # Sin trazas para las consultas del relay: el sondeo se repite cada 0,5 s y cada consulta sería una traza nueva
    # en Tempo (172.800 al día, que llenarían la búsqueda y esconderían las de las peticiones). Lo que importa
    # del relay son los spans "publish", que crea él mismo (suppress_instrumentation no los afecta) y que cuelgan
    # de la petición que hizo el cambio.
    with suppress_instrumentation(), transaction.atomic():
        # SKIP LOCKED: si por error arrancan dos relays, no se esperan el uno al otro… pero ver el módulo 85:
        # con dos relays el orden entre lotes ya no está garantizado. Uno solo.
        lote = list(
            EventoPendiente.objects.select_for_update(skip_locked=True)
            .filter(publicado__isnull=True)
            .order_by("id")[:tamano]
        )
        if not lote:
            return 0

        errores: list = []

        def confirmado(error, mensaje):  # librdkafka la llama desde poll()/flush() con el resultado de cada envío
            if error is not None:
                errores.append(error)

        for ev in lote:
            # La traza de quien hizo el cambio (guardada en el outbox) es la madre de este span: en Grafana,
            # petición → publicación (segundos después) → procesamiento en el otro servicio, todo en una traza.
            madre = propagate.extract({"traceparent": ev.traceparent}) if ev.traceparent else context.Context()
            with tracer.start_as_current_span(
                f"publish {ev.topic}",
                context=madre,
                kind=SpanKind.PRODUCER,
                attributes={
                    "messaging.system": "kafka",
                    "messaging.operation.type": "publish",
                    "messaging.destination.name": ev.topic,
                    "messaging.kafka.message.key": ev.clave,
                    "gastos.evento.tipo": ev.tipo,
                },
            ):
                valor = None if ev.valor is None else json.dumps(ev.valor, separators=(",", ":")).encode()
                productor.produce(
                    ev.topic, key=ev.clave.encode(), value=valor, headers=_cabeceras(ev), on_delivery=confirmado
                )
            productor.poll(0)  # atiende confirmaciones ya llegadas sin bloquear

        sin_confirmar = productor.flush(timeout)  # espera a que Kafka confirme TODO el lote
        if sin_confirmar or errores:
            raise ErrorDePublicacion(f"{sin_confirmar} sin confirmar, {len(errores)} errores: {errores[:3]}")

        ahora = timezone.now()
        EventoPendiente.objects.filter(pk__in=[ev.pk for ev in lote]).update(publicado=ahora)

    for ev in lote:
        retraso.record((ahora - ev.creado).total_seconds(), {"topic": ev.topic})
    publicados.add(len(lote))
    return len(lote)
