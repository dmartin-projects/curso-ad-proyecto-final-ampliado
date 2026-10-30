# asistente/infrastructure/tasks/purgar_conversaciones_task.py — adapter de entrada de Celery Beat (módulo 107)
from celery import shared_task

from asistente.infrastructure import container

PURGAR = "asistente.tasks.purgar_conversaciones"


@shared_task(name=PURGAR, ignore_result=True)
def purgar_conversaciones() -> None:
    container.purgar_conversaciones().ejecutar()
