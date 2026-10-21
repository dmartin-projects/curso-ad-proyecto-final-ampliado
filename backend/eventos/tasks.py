from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import EventoPendiente


@shared_task(ignore_result=True)
def limpiar_eventos_publicados(dias: int = 7) -> int:
    """El outbox no es el histórico (eso es Kafka): los ya publicados se borran pasados unos días.

    Los NO publicados nunca se borran: si se acumulan, el relay está parado y hay que verlo (módulo 85).
    """
    borrados, _ = EventoPendiente.objects.filter(publicado__lt=timezone.now() - timedelta(days=dias)).delete()
    return borrados
