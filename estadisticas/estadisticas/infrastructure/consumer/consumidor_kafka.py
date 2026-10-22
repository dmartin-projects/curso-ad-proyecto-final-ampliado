# estadisticas/infrastructure/consumer/consumidor_kafka.py — el consumidor de Kafka (módulo 85): el adapter de
# ENTRADA que alimenta el use case ProcesarLoteUseCase (módulo 89)
#
# Un proceso aparte de la API: se escala por separado (hasta tantos consumidores como particiones) y si se cae, la
# API sigue respondiendo con los datos que ya tiene.
#
# Ciclo: leer un lote → el use case lo aplica en UNA transacción y la confirma → confirmar a Kafka el offset ("hasta
# aquí he procesado"). Si el proceso muere entre los dos commits, al volver relee ese lote: la proyección es
# idempotente, así que no pasa nada (al menos una vez + idempotencia).
#
# Lo que es de Kafka se queda aquí: crear el Consumer, convertir cada mensaje, confirmar offsets, rebobinar.
import logging
import signal
import threading
from datetime import UTC, datetime

from confluent_kafka import Consumer, KafkaError, Message, TopicPartition

from estadisticas.ajustes import ajustes
from estadisticas.application.procesar_lote_use_case.dtos.procesar_lote_input_dto import ProcesarLoteInputDTO
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO
from estadisticas.domain.exceptions.esquema_desconocido_exception import EsquemaDesconocidoException
from estadisticas.infrastructure import container
from estadisticas.infrastructure.messaging.aparcados_kafka import asegurar_topic
from estadisticas.infrastructure.telemetry import telemetria

logger = logging.getLogger("estadisticas.consumidor")


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


def a_mensaje(msg: Message) -> MensajeInputDTO:
    """De confluent_kafka.Message al InputDTO del use case."""
    _tipo, marca_ms = msg.timestamp()
    return MensajeInputDTO(
        topic=msg.topic(),
        particion=msg.partition(),
        offset=msg.offset(),
        clave=msg.key().decode(),
        valor=msg.value(),
        marca=datetime.fromtimestamp(marca_ms / 1000, UTC),
        cabeceras={k: v.decode() for k, v in (msg.headers() or [])},
    )


def _rebobinar(consumidor: Consumer, mensajes: list[Message]) -> None:
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
    asegurar_topic(a.kafka_bootstrap_servers, a.topic_dlq)
    procesar = container.procesar_lote()  # el use case, montado por el composition root
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
                n = procesar.ejecutar(ProcesarLoteInputDTO(mensajes=[a_mensaje(m) for m in mensajes if not m.error()]))
            except EsquemaDesconocidoException:
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
