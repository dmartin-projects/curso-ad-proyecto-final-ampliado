# asistente/infrastructure/messaging/programador_de_analisis_celery.py — el análisis, a Celery (módulo 105)
from celery import current_app
from django.db import transaction

from asistente.application.ports.i_programador_de_analisis import IProgramadorDeAnalisis

ANALIZAR = "asistente.tasks.analizar_mes"


class ProgramadorDeAnalisisCelery(IProgramadorDeAnalisis):
    """En la cola "default", con on_commit y por su nombre, como la compactación (módulo 99)."""

    def programar(self, usuario_id, hogar_id, mes, tarea):
        transaction.on_commit(lambda: current_app.tasks[ANALIZAR].delay(usuario_id, hogar_id, mes, tarea))
