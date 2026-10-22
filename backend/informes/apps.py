from django.apps import AppConfig


class InformesConfig(AppConfig):
    name = "informes"

    def ready(self):
        # Las tareas de Celery: Celery solo busca <app>.tasks y las nuestras están en infrastructure/tasks/ (módulo 87)
        from .infrastructure.tasks import (  # noqa: F401
            enviar_informe_task,
            generar_informe_task,
            generar_informes_mensuales_task,
        )
