"""El consumidor de Kafka (módulo 85): `python -m estadisticas.consumidor`.

Un proceso aparte de la API: se escala por separado (hasta tantos consumidores como particiones) y si se
cae, la API sigue respondiendo con los datos que ya tiene.

Ciclo: leer un lote → aplicarlo en UNA transacción de PostgreSQL → confirmar la transacción → confirmar a
Kafka el offset ("hasta aquí he procesado"). Si el proceso muere entre los dos commits, al volver relee
ese lote: la proyección es idempotente, así que no pasa nada (al menos una vez + idempotencia).
"""

import logging
import signal
import threading
from datetime import UTC, datetime

from confluent_kafka import Consumer, KafkaError, TopicPartition
from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind
from sqlalchemy.dialects.postgresql import insert

from . import telemetria
from .ajustes import ajustes
from .bd import Progreso, sesion
from .proyeccion import EsquemaDesconocido, aplicar

logger = logging.getLogger("estadisticas.consumidor")
tracer = trace.get_tracer("estadisticas.consumidor")


def crear_consumidor() -> Consumer:
    a = ajustes()
    return Consumer(
        {
            "bootstrap.servers": a.kafka_bootstrap_servers,
            "group.id": a.kafka_grupo,
            "client.id": "estadisticas",
            # Sin offset guardado para el grupo (la primera vez, o tras reconstruir): desde el principio
            "auto.offset.reset": "earliest",
            # Los offsets los confirmamos NOSOTROS, después de guardar en PostgreSQL. Con el autocommit,
            # Kafka podría dar por leído un mensaje que todavía no está en la base de datos.
            "enable.auto.commit": False,
            # Reparto incremental: al entrar o salir un consumidor, solo se mueven las particiones necesarias
            "partition.assignment.strategy": "cooperative-sticky",
        }
    )


def _cabeceras(msg) -> dict[str, str]:
    return {k: v.decode() for k, v in (msg.headers() or [])}


def procesar_lote(mensajes) -> int:
    """Aplica un lote en una transacción. Devuelve cuántos mensajes válidos había."""
    validos = [m for m in mensajes if not m.error()]
    progreso: dict[tuple[str, int], tuple[int, datetime]] = {}
    with sesion() as s, s.begin():
        for msg in validos:
            cabeceras = _cabeceras(msg)
            # Este span cuelga del de publicación del relay, que cuelga de la petición que hizo el cambio
            with tracer.start_as_current_span(
                f"process {msg.topic()}",
                context=propagate.extract(cabeceras),
                kind=SpanKind.CONSUMER,
                attributes={
                    "messaging.system": "kafka",
                    "messaging.operation.type": "process",
                    "messaging.destination.name": msg.topic(),
                    "messaging.destination.partition.id": str(msg.partition()),
                    "messaging.kafka.offset": msg.offset(),
                    "messaging.kafka.message.key": msg.key().decode(),
                },
            ) as span:
                resultado = aplicar(s, msg.topic(), msg.key().decode(), msg.value(), cabeceras)
                span.set_attribute("estadisticas.resultado", resultado)
            _tipo, marca_ms = msg.timestamp()
            progreso[(msg.topic(), msg.partition())] = (msg.offset(), datetime.fromtimestamp(marca_ms / 1000, UTC))
        for (topic, particion), (offset, marca) in progreso.items():
            fila = insert(Progreso).values(topic=topic, particion=particion, offset=offset, marca=marca)
            s.execute(fila.on_conflict_do_update(index_elements=["topic", "particion"], set_=fila.excluded))
    return len(validos)


def _rebobinar(consumidor: Consumer, mensajes) -> None:
    """Tras un fallo, vuelve al primer mensaje del lote en cada partición: sin esto, el siguiente consume()
    seguiría DESPUÉS del lote fallido y esos mensajes se perderían hasta reiniciar el proceso."""
    primeros: dict[tuple[str, int], int] = {}
    for m in mensajes:
        if not m.error():
            clave = (m.topic(), m.partition())
            primeros[clave] = min(primeros.get(clave, m.offset()), m.offset())
    for (topic, particion), offset in primeros.items():
        consumidor.seek(TopicPartition(topic, particion, offset))


def ejecutar(parar: threading.Event, consumidor: Consumer | None = None) -> None:
    a = ajustes()
    consumidor = consumidor or crear_consumidor()
    consumidor.subscribe([a.topic_movimientos, a.topic_membresias])
    espera = 1.0
    try:
        while not parar.is_set():
            mensajes = consumidor.consume(num_messages=500, timeout=1.0)
            if not mensajes:
                continue
            for m in mensajes:
                if m.error() and m.error().code() != KafkaError._PARTITION_EOF:
                    logger.error("Error de Kafka: %s", m.error())
            try:
                n = procesar_lote(mensajes)
            except EsquemaDesconocido:
                # Un formato nuevo que este servicio no entiende: parar en vez de saltárselo en silencio.
                # Se actualiza el servicio y, al volver, sigue por aquí (el offset no se ha confirmado).
                logger.exception("Mensaje con un esquema desconocido: el consumidor se detiene")
                raise
            except Exception:  # PostgreSQL caído, un bug…: nada confirmado ni en la BD ni en Kafka
                logger.exception("No se pudo aplicar el lote; reintento en %.0f s", espera)
                _rebobinar(consumidor, mensajes)
                parar.wait(espera)
                espera = min(espera * 2, 30)
                continue
            espera = 1.0
            consumidor.commit(asynchronous=False)  # DESPUÉS de confirmar en PostgreSQL
            logger.info("Aplicados %s eventos", n)
    finally:
        consumidor.close()  # avisa al grupo: sus particiones pasan a otro consumidor sin esperar


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    telemetria.configurar("estadisticas-consumidor")
    parar = threading.Event()
    for senal in (signal.SIGTERM, signal.SIGINT):
        signal.signal(senal, lambda *_: parar.set())
    ejecutar(parar)


if __name__ == "__main__":
    main()
