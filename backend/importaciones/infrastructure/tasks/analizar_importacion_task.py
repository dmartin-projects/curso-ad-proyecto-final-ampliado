# importaciones/infrastructure/tasks/analizar_importacion_task.py — adapter de entrada de Celery (módulos 26, 75 y 88)
# name= explícito (módulo 87): los nombres de siempre. El chord los referencia por nombre (messaging/) y los
# mensajes que ya estén en RabbitMQ al desplegar los siguen encontrando.
from celery import shared_task

from importaciones.application.analizar_extracto_use_case.dtos.analizar_extracto_input_dto import (
    AnalizarExtractoInputDTO,
)
from importaciones.infrastructure import container
from importaciones.infrastructure.messaging.publicador_eventos_django import ANALIZAR
from importaciones.infrastructure.tasks.tarea_importacion import TareaImportacion


@shared_task(name=ANALIZAR, base=TareaImportacion, acks_late=True)
def analizar_importacion(importacion_id: int) -> None:
    container.analizar_extracto().ejecutar(AnalizarExtractoInputDTO(importacion_id))
