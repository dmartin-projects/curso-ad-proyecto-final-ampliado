# estadisticas/infrastructure/messaging/grupo_kafka.py — IGrupoDeConsumidores con el AdminClient de Kafka, para
# reconstruir (módulos 85 y 89)
from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient

from estadisticas.application.ports.i_grupo_de_consumidores import IGrupoDeConsumidores
from estadisticas.domain.exceptions.consumidor_activo_exception import ConsumidorActivoException


class GrupoKafka(IGrupoDeConsumidores):
    def __init__(self, servidores: str, grupo: str):
        self.servidores = servidores
        self.grupo = grupo

    def olvidar(self) -> None:
        """Borra el grupo en Kafka: sin offsets guardados, `auto.offset.reset=earliest` lo pondrá a leer desde
        el principio de los topics compactados, que guardan el último estado de cada movimiento."""
        admin = AdminClient({"bootstrap.servers": self.servidores})
        try:
            admin.delete_consumer_groups([self.grupo], request_timeout=15)[self.grupo].result()
        except KafkaException as e:
            codigo = e.args[0].code()
            if codigo == KafkaError.NON_EMPTY_GROUP:  # Kafka no deja borrar un grupo con consumidores conectados
                raise ConsumidorActivoException("Para el consumidor antes de reconstruir") from e
            if codigo != KafkaError.GROUP_ID_NOT_FOUND:  # no existía: nada que olvidar
                raise
