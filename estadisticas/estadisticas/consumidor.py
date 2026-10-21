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

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic
from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DataError, IntegrityError

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


# ── Ejercicio 3: mensajes venenosos → topic de "aparcados" (dead letter queue) ──
# Un mensaje que NUNCA se va a poder aplicar (JSON roto, un importe "abc", falta un campo) bloquearía su
# partición para siempre: falla, se rebobina, vuelve a fallar… Se aparca en otro topic, con el error, y se
# sigue. Los fallos PASAJEROS (PostgreSQL caído: OperationalError) no son venenosos: esos se reintentan.
VENENOSOS = (ValueError, KeyError, TypeError, ArithmeticError, DataError, IntegrityError)
_productor: Producer | None = None


def _productor_dlq() -> Producer:
    global _productor
    if _productor is None:
        _productor = Producer({"bootstrap.servers": ajustes().kafka_bootstrap_servers, "enable.idempotence": True})
    return _productor


def asegurar_dlq() -> None:
    """El topic de aparcados es cosa del consumidor: lo crea él al arrancar (si no existe)."""
    a = ajustes()
    admin = AdminClient({"bootstrap.servers": a.kafka_bootstrap_servers})
    nuevo = NewTopic(a.topic_dlq, num_partitions=1, replication_factor=1, config={"retention.ms": str(30 * 86_400_000)})
    try:
        admin.create_topics([nuevo])[a.topic_dlq].result()
    except KafkaException as e:
        if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
            raise


def _aparcar(msg, error: Exception) -> None:
    cabeceras = list(msg.headers() or []) + [
        ("error", repr(error)[:500].encode()),
        ("origen", f"{msg.topic()}/{msg.partition()}/{msg.offset()}".encode()),
    ]
    _productor_dlq().produce(ajustes().topic_dlq, key=msg.key(), value=msg.value(), headers=cabeceras)
    logger.error("Mensaje aparcado %s/%s/%s: %r", msg.topic(), msg.partition(), msg.offset(), error)


class _HayVenenosos(Exception):
    pass


def procesar_lote(mensajes) -> int:
    """Aplica un lote en una transacción. Devuelve cuántos mensajes válidos había.

    Primero, el lote entero de una vez (lo normal: rápido). Solo si algún mensaje es venenoso, se repite el
    lote mensaje a mensaje con un SAVEPOINT cada uno, para aparcar los malos y aplicar los buenos. Medido con
    20.000 mensajes: con SAVEPOINT siempre, 34 s; así, 21 s (el SAVEPOINT por mensaje cuesta un 60 %).
    """
    validos = [m for m in mensajes if not m.error()]
    try:
        _aplicar(validos, con_cuidado=False)
    except _HayVenenosos:
        _aplicar(validos, con_cuidado=True)  # la transacción anterior se deshizo entera: no queda nada a medias
    return len(validos)


def _aplicar(validos, *, con_cuidado: bool) -> None:
    progreso: dict[tuple[str, int], tuple[int, datetime]] = {}
    aparcados = 0
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
                if not con_cuidado:
                    try:
                        resultado = aplicar(s, msg.topic(), msg.key().decode(), msg.value(), cabeceras)
                    except VENENOSOS as e:
                        raise _HayVenenosos from e  # deshace el lote y se repite con cuidado
                else:
                    try:
                        with s.begin_nested():  # SAVEPOINT: si este mensaje falla, se deshace solo él
                            resultado = aplicar(s, msg.topic(), msg.key().decode(), msg.value(), cabeceras)
                    except VENENOSOS as e:
                        _aparcar(msg, e)
                        aparcados += 1
                        resultado = "aparcado"
                span.set_attribute("estadisticas.resultado", resultado)
            _tipo, marca_ms = msg.timestamp()
            progreso[(msg.topic(), msg.partition())] = (msg.offset(), datetime.fromtimestamp(marca_ms / 1000, UTC))
        for (topic, particion), (offset, marca) in progreso.items():
            fila = insert(Progreso).values(topic=topic, particion=particion, offset=offset, marca=marca)
            s.execute(fila.on_conflict_do_update(index_elements=["topic", "particion"], set_=fila.excluded))
        # Antes de confirmar nada: los aparcados tienen que estar a salvo en Kafka. Si no, excepción → el
        # lote se repite (y quizá se aparquen dos veces: mejor eso que perder el mensaje)
        if aparcados and _productor_dlq().flush(10):
            raise RuntimeError("No se pudieron guardar los mensajes aparcados")


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
    asegurar_dlq()
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
