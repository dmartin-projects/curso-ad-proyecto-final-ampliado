# importaciones/infrastructure/tasks/finalizar_importacion_task.py — adapters de entrada de Celery: el cierre del chord (bien o mal) (módulos 26, 75 y 88)
# name= explícito (módulo 87): los nombres de siempre. El chord los referencia por nombre (messaging/) y los
# mensajes que ya estén en RabbitMQ al desplegar los siguen encontrando.
from celery import shared_task

from importaciones.application.fallar_importacion_use_case.dtos.fallar_importacion_input_dto import (
    FallarImportacionInputDTO,
)
from importaciones.application.finalizar_importacion_use_case.dtos.finalizar_importacion_input_dto import (
    FinalizarImportacionInputDTO,
)
from importaciones.infrastructure import container
from importaciones.infrastructure.messaging.publicador_eventos_django import FALLIDA, FINALIZAR


@shared_task(name=FINALIZAR, acks_late=True)
def finalizar_importacion(importacion_id: int) -> None:
    container.finalizar_importacion().ejecutar(FinalizarImportacionInputDTO(importacion_id))


@shared_task(name=FALLIDA)
def importacion_fallida(importacion_id: int) -> None:
    mensaje = "No se pudieron importar todos los movimientos. Puedes deshacer y repetir."
    container.fallar_importacion().ejecutar(FallarImportacionInputDTO(importacion_id, mensaje))
