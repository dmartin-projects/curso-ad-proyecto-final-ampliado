"""El relay del outbox como proceso (módulo 85): `manage.py publicar_eventos`. UNO por despliegue."""

import logging
import signal
import threading

from confluent_kafka import KafkaException
from django.core.management.base import BaseCommand
from django.db import DatabaseError, close_old_connections
from opentelemetry.instrumentation.utils import suppress_instrumentation

from eventos.domain.exceptions.publicacion_no_confirmada_exception import PublicacionNoConfirmadaException
from eventos.infrastructure.messaging.kafka import productor
from eventos.infrastructure.relay.publicar_lote import publicar_lote

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Publica en Kafka los eventos del outbox. Corre hasta recibir SIGTERM (docker stop)."

    def add_arguments(self, parser):
        parser.add_argument("--intervalo", type=float, default=0.5, help="Segundos de espera si no hay nada")
        parser.add_argument("--lote", type=int, default=500)
        parser.add_argument("--una-vez", action="store_true", help="Publica lo pendiente y termina")

    def handle(self, *args, intervalo, lote, una_vez, **opciones):
        parar = threading.Event()
        for senal in (signal.SIGTERM, signal.SIGINT):  # docker stop manda SIGTERM: terminar el lote y salir
            signal.signal(senal, lambda *_: parar.set())

        kafka = productor()
        espera_por_error = 1.0
        total = 0
        while not parar.is_set():
            with suppress_instrumentation():  # su "SELECT 1" (CONN_HEALTH_CHECKS), cada 0,5 s, tampoco a Tempo
                close_old_connections()  # proceso de larga vida: si PostgreSQL se reinició, reconecta
            try:
                n = publicar_lote(kafka, tamano=lote)
            except (PublicacionNoConfirmadaException, KafkaException, DatabaseError) as e:
                # Kafka o PostgreSQL caídos: nada se ha marcado. Esperar cada vez más (máximo 30 s) y reintentar
                logger.warning("No se pudo publicar el lote (%s); reintento en %.0f s", e, espera_por_error)
                parar.wait(espera_por_error)
                espera_por_error = min(espera_por_error * 2, 30)
                continue
            espera_por_error = 1.0
            total += n
            if n:
                logger.info("Publicados %s eventos", n)
            if una_vez and n < lote:
                break
            if n < lote:  # lote incompleto: no queda nada; si estaba lleno, seguir sin esperar
                parar.wait(intervalo)

        kafka.flush(10)
        self.stdout.write(f"Relay detenido ({total} eventos publicados)")
