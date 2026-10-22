# estadisticas/infrastructure/messaging/aparcados_kafka.py — IAparcados con un topic de Kafka, la dead letter queue
# (módulo 85, ejercicio 3; aquí desde el 89)
#
# Un mensaje que NUNCA se va a poder aplicar bloquearía su partición para siempre (falla, se rebobina, vuelve a
# fallar…). Se aparca en otro topic, con el error y de dónde venía, y se sigue.
import logging

from confluent_kafka import KafkaError, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from estadisticas.application.ports.i_aparcados import IAparcados
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO

logger = logging.getLogger("estadisticas.consumidor")


def asegurar_topic(servidores: str, topic: str) -> None:
    """El topic de aparcados es cosa del consumidor: lo crea él al arrancar (si no existe)."""
    admin = AdminClient({"bootstrap.servers": servidores})
    nuevo = NewTopic(topic, num_partitions=1, replication_factor=1, config={"retention.ms": str(30 * 86_400_000)})
    try:
        admin.create_topics([nuevo])[topic].result()
    except KafkaException as e:
        if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
            raise


class AparcadosKafka(IAparcados):
    def __init__(self, servidores: str, topic: str):
        self.servidores = servidores
        self.topic = topic
        self._productor: Producer | None = None  # se crea al aparcar el primero: casi nunca hace falta

    def _producir(self) -> Producer:
        if self._productor is None:
            self._productor = Producer({"bootstrap.servers": self.servidores, "enable.idempotence": True})
        return self._productor

    def aparcar(self, mensaje: MensajeInputDTO, error: Exception) -> None:
        cabeceras = [(k, v.encode()) for k, v in mensaje.cabeceras.items()] + [
            ("error", repr(error)[:500].encode()),
            ("origen", f"{mensaje.topic}/{mensaje.particion}/{mensaje.offset}".encode()),
        ]
        self._producir().produce(self.topic, key=mensaje.clave.encode(), value=mensaje.valor, headers=cabeceras)
        logger.error("Mensaje aparcado %s/%s/%s: %r", mensaje.topic, mensaje.particion, mensaje.offset, error)

    def confirmar(self) -> None:
        if self._producir().flush(10):  # flush devuelve cuántos quedan sin entregar
            raise RuntimeError("No se pudieron guardar los mensajes aparcados")
