"""Crea los topics de Gastos con su configuración (módulo 85). Se puede repetir: los que existen no se tocan."""

from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import NewTopic
from django.core.management.base import BaseCommand, CommandError

from eventos.infrastructure.messaging.kafka import TOPICS, admin


class Command(BaseCommand):
    help = "Crea los topics de Kafka de Gastos si no existen (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument("--replicas", type=int, default=1, help="Factor de replicación (1 con un solo broker)")

    def handle(self, *args, replicas, **opciones):
        cliente = admin()
        nuevos = [
            NewTopic(nombre, num_partitions=t["particiones"], replication_factor=replicas, config=t["config"])
            for nombre, t in TOPICS.items()
        ]
        for nombre, futuro in cliente.create_topics(nuevos, request_timeout=15).items():
            try:
                futuro.result()
                self.stdout.write(self.style.SUCCESS(f"Creado {nombre}"))
            except KafkaException as e:
                if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                    raise CommandError(f"{nombre}: {e}") from e
                self._comprobar(cliente, nombre)

    def _comprobar(self, cliente, nombre: str) -> None:
        """Ya existía: avisa si tiene otras particiones (no se cambian solas, ver el módulo 85)."""
        info = cliente.list_topics(nombre, timeout=10).topics[nombre]
        esperadas = TOPICS[nombre]["particiones"]
        if len(info.partitions) != esperadas:
            self.stdout.write(
                self.style.WARNING(
                    f"{nombre} ya existe con {len(info.partitions)} particiones (se esperaban {esperadas})"
                )
            )
        else:
            self.stdout.write(f"{nombre} ya existe")
