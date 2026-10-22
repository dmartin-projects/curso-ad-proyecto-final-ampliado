# importaciones/infrastructure/tasks/tarea_importacion.py — la base de las tareas de una importación (módulos 75 y 88)
import logging

from celery import Task

from importaciones.application.fallar_importacion_use_case.dtos.fallar_importacion_input_dto import (
    FallarImportacionInputDTO,
)
from importaciones.infrastructure import container

logger = logging.getLogger(__name__)


class TareaImportacion(Task):
    """Si una tarea de la importación falla del todo, la importación acaba en error."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.warning("Importación %s fallida en %s: %r", args[0], self.name, exc)
        entrada = FallarImportacionInputDTO(args[0], "Error inesperado al procesar el archivo.")
        container.fallar_importacion().ejecutar(entrada)
