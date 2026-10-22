# eventos/infrastructure/tasks/limpiar_eventos_publicados_task.py — mantenimiento del outbox (módulos 85 y 88)
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from eventos.infrastructure.database.models.evento_pendiente_model import EventoPendiente as EventoPendienteModel


@shared_task(name="eventos.tasks.limpiar_eventos_publicados", ignore_result=True)  # el de CELERY_BEAT_SCHEDULE
def limpiar_eventos_publicados(dias: int = 7) -> int:
    """El outbox no es el histórico (eso es Kafka): los ya publicados se borran pasados unos días.

    Los NO publicados nunca se borran: si se acumulan, el relay está parado y hay que verlo (módulo 85).
    """
    borrados, _ = EventoPendienteModel.objects.filter(publicado__lt=timezone.now() - timedelta(days=dias)).delete()
    return borrados
