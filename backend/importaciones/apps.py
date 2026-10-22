from django.apps import AppConfig


class ImportacionesConfig(AppConfig):
    name = "importaciones"

    def ready(self):
        # Las tareas de Celery: Celery solo busca <app>.tasks y las nuestras están en infrastructure/tasks/ (módulo 87)
        from .infrastructure.tasks import (  # noqa: F401
            analizar_importacion_task,
            finalizar_importacion_task,
            importar_lote_task,
        )
