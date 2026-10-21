"""Módulo 85, ejercicio 2: el retraso del consumidor (lag), medido DESDE FUERA del consumidor.

Retraso de una partición = último offset escrito (high watermark) − último offset confirmado por el grupo.
Lo mide la API, no el consumidor: si el consumidor se cae, es justo cuando el retraso crece, y un
consumidor muerto no puede contar nada. Es lo mismo que enseña `kafka-consumer-groups.sh --describe`.
"""

import logging

from confluent_kafka import ConsumerGroupTopicPartitions, TopicPartition
from confluent_kafka.admin import AdminClient, OffsetSpec

from .ajustes import ajustes

logger = logging.getLogger(__name__)


def retraso(timeout: float = 5) -> dict[str, int]:
    """{topic: mensajes pendientes de procesar por el grupo}, sumando sus particiones."""
    a = ajustes()
    admin = AdminClient({"bootstrap.servers": a.kafka_bootstrap_servers})
    topics = [a.topic_movimientos, a.topic_membresias]

    grupo = ConsumerGroupTopicPartitions(a.kafka_grupo)
    confirmados = {
        (tp.topic, tp.partition): tp.offset
        for tp in admin.list_consumer_group_offsets([grupo], request_timeout=timeout)[a.kafka_grupo]
        .result()
        .topic_partitions
    }
    meta = admin.list_topics(timeout=timeout).topics
    particiones = [TopicPartition(t, p) for t in topics for p in meta[t].partitions]
    finales = admin.list_offsets({tp: OffsetSpec.latest() for tp in particiones}, request_timeout=timeout)
    iniciales = admin.list_offsets({tp: OffsetSpec.earliest() for tp in particiones}, request_timeout=timeout)

    resultado = dict.fromkeys(topics, 0)
    for tp, futuro in finales.items():
        fin = futuro.result().offset
        # Sin offset confirmado (grupo nuevo o tras reconstruir), todo lo que queda en el topic está pendiente
        confirmado = confirmados.get((tp.topic, tp.partition), -1)
        desde = confirmado if confirmado >= 0 else iniciales[tp].result().offset
        resultado[tp.topic] += max(fin - desde, 0)
    return resultado


def registrar_metrica() -> None:
    """Un gauge observable: el SDK lo lee al exportar (cada OTEL_METRIC_EXPORT_INTERVAL ms)."""
    from opentelemetry import metrics
    from opentelemetry.metrics import Observation

    def observar(_opciones):
        try:
            for topic, pendientes in retraso(timeout=3).items():
                yield Observation(pendientes, {"topic": topic})
        except Exception:  # Kafka caído: sin dato (la alerta de "sin datos" lo cubre), no un 0 falso
            logger.warning("No se pudo medir el retraso del consumidor", exc_info=True)

    metrics.get_meter("estadisticas").create_observable_gauge(
        "estadisticas.consumidor.retraso",
        callbacks=[observar],
        unit="{mensaje}",
        description="Mensajes de Kafka que el consumidor de estadísticas aún no ha procesado",
    )
