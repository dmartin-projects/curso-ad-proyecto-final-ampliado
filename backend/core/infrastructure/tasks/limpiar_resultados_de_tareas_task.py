# core/infrastructure/tasks/limpiar_resultados_de_tareas_task.py — mantenimiento de django.tasks (módulos 26 y 88)
from celery import shared_task
from django.core.management import call_command


# name= explícito: el nombre de siempre, el que usa CELERY_BEAT_SCHEDULE (core.tasks.…)
@shared_task(name="core.tasks.limpiar_resultados_de_tareas", ignore_result=True)
def limpiar_resultados_de_tareas() -> None:
    """Los resultados de django.tasks se guardan en la BD (django-tasks-db): sin limpiar, la tabla crece sin fin."""
    call_command("prune_db_task_results", queue_name="*", min_age_days=14, failed_min_age_days=30)
