# asistente/infrastructure/messaging/programador_de_compactacion_celery.py — la compactación, a Celery (módulo 99)
from celery import current_app
from django.db import transaction

from asistente.application.ports.i_programador_de_compactacion import IProgramadorDeCompactacion

COMPACTAR = "asistente.tasks.compactar_conversacion"


class ProgramadorDeCompactacionCelery(IProgramadorDeCompactacion):
    """Con on_commit, como los eventos de tickets (módulo 88): la tarea lee la respuesta recién guardada, así que solo
    se encola cuando está guardada de verdad. Por su nombre: este adapter no importa el de entrada (la tarea)."""

    def programar(self, usuario_id, hogar_id, conversacion_id):
        transaction.on_commit(lambda: current_app.tasks[COMPACTAR].delay(usuario_id, hogar_id, conversacion_id))
