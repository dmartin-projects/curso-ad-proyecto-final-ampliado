"""Clientes de Kafka (confluent-kafka, que envuelve librdkafka, el cliente en C de referencia)."""

from django.conf import settings


def config_base() -> dict:
    return {
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "client.id": "gastos-django",
    }


def productor():
    from confluent_kafka import Producer

    return Producer(
        {
            **config_base(),
            # Idempotente: si un envío se reintenta (se cortó la red tras llegar al broker), el broker
            # descarta la copia. Sin duplicados por reintentos y con el orden de la partición intacto.
            # Implica acks=all: el broker confirma cuando el mensaje está en todas las réplicas en sincronía.
            "enable.idempotence": True,
            "acks": "all",
            "linger.ms": 20,  # espera hasta 20 ms para juntar mensajes en un lote (menos peticiones)
            "compression.type": "zstd",
            "delivery.timeout.ms": 30_000,  # si en 30 s no se ha podido entregar, el envío falla
        }
    )


def admin():
    from confluent_kafka.admin import AdminClient

    return AdminClient(config_base())
