# importaciones/infrastructure/tasks/importar_lote_task.py — adapter de entrada de Celery: un lote del chord (módulos 26, 75 y 88)
# name= explícito (módulo 87): los nombres de siempre. El chord los referencia por nombre (messaging/) y los
# mensajes que ya estén en RabbitMQ al desplegar los siguen encontrando.
from celery import shared_task
from django.db import IntegrityError, OperationalError

from importaciones.application.importar_lote_use_case.dtos.importar_lote_input_dto import ImportarLoteInputDTO
from importaciones.infrastructure import container
from importaciones.infrastructure.messaging.publicador_eventos_django import LOTE
from importaciones.infrastructure.tasks.tarea_importacion import TareaImportacion


@shared_task(
    name=LOTE,
    base=TareaImportacion,
    acks_late=True,
    # IntegrityError: un extracto solapado creó la misma huella a la vez → el reintento la verá como duplicada
    autoretry_for=(IntegrityError, OperationalError),
    retry_backoff=5,
    max_retries=3,
)
def importar_lote(importacion_id: int, ids: list[int]) -> dict:
    return container.importar_lote().ejecutar(ImportarLoteInputDTO(importacion_id, ids))
