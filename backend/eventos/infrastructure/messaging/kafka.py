# eventos/infrastructure/messaging/kafka.py — los clientes y los topics de Kafka (módulos 85 y 88)
#
# confluent-kafka envuelve librdkafka, el cliente en C de referencia.
from django.conf import settings

from eventos.domain.services.mensajes import MEMBRESIAS, MOVIMIENTOS

# ── Los topics (los crea `manage.py crear_topics`: el broker tiene desactivada la creación automática) ──
# Topics COMPACTADOS: Kafka guarda, para cada clave, al menos el ÚLTIMO mensaje (y borra los anteriores
# poco a poco). Con la clave = id del objeto, el topic es una copia del estado actual de todos los
# objetos: un consumidor nuevo lo lee desde el principio y reconstruye su base de datos entera.
# Un mensaje con valor nulo ("tombstone") dice "este objeto ya no existe"; se borra pasado delete.retention.ms.
COMPACTADO = {
    "cleanup.policy": "compact",
    "min.cleanable.dirty.ratio": "0.1",  # compacta cuando el 10 % del topic son versiones viejas
    "segment.ms": str(24 * 3600 * 1000),  # el segmento activo no se compacta: se cierra cada día
    "delete.retention.ms": str(7 * 24 * 3600 * 1000),  # los tombstones viven 7 días: da tiempo a verlos
}

TOPICS = {
    # 3 particiones: hasta 3 consumidores del mismo grupo leyendo en paralelo. El orden se garantiza
    # DENTRO de una partición; como la clave es el id del movimiento, todas las versiones de un
    # movimiento van a la misma partición y se leen en el orden en que se publicaron.
    MOVIMIENTOS: {"particiones": 3, "config": COMPACTADO},
    MEMBRESIAS: {"particiones": 1, "config": COMPACTADO},
}


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
