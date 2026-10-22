# estadisticas/infrastructure/consumer/reintentos_kafka.py — reintentar los mensajes aparcados (módulo 89,
# ejercicio 1): `python -m estadisticas.reintentar`
#
# Un segundo adapter de entrada para el MISMO use case que el consumidor (ProcesarLoteUseCase). Lee el topic de
# aparcados desde donde se quedó la última vez (su propio consumer group), devuelve cada mensaje a su forma original
# (topic, partición y offset de la cabecera "origen"; sin "error" ni "origen") y lo aplica. Para cuando se ha
# desplegado el arreglo de lo que hacía fallar esos mensajes.
#
# Se puede lanzar cuando se quiera: la proyección es idempotente por versión, así que un aparcado más viejo que lo
# que ya hay se ignora. Lo que vuelva a fallar se aparca otra vez, al final del topic, y no se relee en esta pasada:
# se lee hasta el final que había al empezar.
import logging
import time
from datetime import UTC, datetime

from confluent_kafka import Consumer, Message, TopicPartition

from estadisticas.ajustes import ajustes
from estadisticas.application.procesar_lote_use_case.dtos.procesar_lote_input_dto import ProcesarLoteInputDTO
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO
from estadisticas.infrastructure import container


def a_mensaje_original(msg: Message) -> MensajeInputDTO:
    cabeceras = {k: v.decode() for k, v in (msg.headers() or [])}
    topic, particion, offset = cabeceras.pop("origen").rsplit("/", 2)
    cabeceras.pop("error", None)
    _tipo, marca_ms = msg.timestamp()
    return MensajeInputDTO(
        topic=topic,
        particion=int(particion),
        offset=int(offset),
        clave=msg.key().decode(),
        valor=msg.value(),
        marca=datetime.fromtimestamp(marca_ms / 1000, UTC),
        cabeceras=cabeceras,
    )


def reintentar(espera_maxima: float = 30) -> int:
    """Reintenta los aparcados pendientes. Devuelve cuántos ha procesado (aplicados, ignorados o reaparcados)."""
    a = ajustes()
    consumidor = Consumer(
        {
            "bootstrap.servers": a.kafka_bootstrap_servers,
            "group.id": f"{a.kafka_grupo}-reintentos",
            "enable.auto.commit": False,
        }
    )
    try:
        meta = consumidor.list_topics(a.topic_dlq, timeout=10).topics[a.topic_dlq]
        particiones = [TopicPartition(a.topic_dlq, p) for p in meta.partitions]
        # Hasta dónde leer: el final de AHORA (lo que se reaparque en esta pasada queda detrás)
        limites = {tp.partition: consumidor.get_watermark_offsets(tp, timeout=10) for tp in particiones}
        finales = {p: fin for p, (_inicio, fin) in limites.items()}
        asignar = []
        for tp in consumidor.committed(particiones, timeout=10):
            desde = tp.offset if tp.offset >= 0 else limites[tp.partition][0]  # sin nada confirmado: el principio
            if desde < finales[tp.partition]:
                asignar.append(TopicPartition(a.topic_dlq, tp.partition, desde))
        if not asignar:
            return 0
        consumidor.assign(asignar)  # sin subscribe: no hace falta esperar al reparto del grupo
        procesar, total = container.procesar_lote(), 0
        pendientes = {tp.partition for tp in asignar}
        limite = time.monotonic() + espera_maxima
        while pendientes and time.monotonic() < limite:
            lote = [
                m
                for m in consumidor.consume(num_messages=500, timeout=1.0)
                if not m.error() and m.partition() in pendientes and m.offset() < finales[m.partition()]
            ]
            if not lote:
                continue
            # Sin anotar progreso: estos mensajes no son la cabeza de su partición (haría retroceder la marca)
            procesar.ejecutar(
                ProcesarLoteInputDTO(mensajes=[a_mensaje_original(m) for m in lote], anotar_progreso=False)
            )
            ultimos = {m.partition(): m.offset() for m in lote}
            consumidor.commit(
                offsets=[TopicPartition(a.topic_dlq, p, o + 1) for p, o in ultimos.items()], asynchronous=False
            )
            total += len(lote)
            pendientes -= {p for p, o in ultimos.items() if o + 1 >= finales[p]}
        return total
    finally:
        consumidor.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    print(f"Reintentados {reintentar()} mensajes aparcados.")
