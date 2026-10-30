# asistente/infrastructure/tasks/compactar_conversacion_task.py — adapter de entrada de Celery (módulo 99)
from celery import shared_task

from asistente.application.compactar_conversacion_use_case.dtos.compactar_conversacion_input_dto import (
    CompactarConversacionInputDTO,
)
from asistente.domain.exceptions.conversacion_no_encontrada_exception import ConversacionNoEncontradaException
from asistente.infrastructure import container
from asistente.infrastructure.messaging.programador_de_compactacion_celery import COMPACTAR


# Sin reintentos: si el modelo no está, se intentará tras la próxima respuesta (y mientras, la ventana quita lo
# antiguo). Un resumen no es urgente; un reintento en bucle contra un 429 sí sería un problema.
@shared_task(name=COMPACTAR, ignore_result=True)
def compactar_conversacion(usuario_id: int, hogar_id: int, conversacion_id: int) -> None:
    try:
        container.compactar_conversacion().ejecutar(
            CompactarConversacionInputDTO(usuario_id, hogar_id, conversacion_id)
        )
    except ConversacionNoEncontradaException:  # borrada entre la respuesta y la tarea: nada que resumir
        pass
