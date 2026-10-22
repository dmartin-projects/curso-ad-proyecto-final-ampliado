from django.apps import AppConfig


class FinanzasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finanzas"

    def ready(self):
        # Los adapters de entrada que Django y Celery no descubren solos (módulo 87): los receivers (se conectan
        # al importarse) y las tareas (Celery solo busca <app>.tasks y las nuestras están en infrastructure/tasks/)
        from .infrastructure.signals import receivers  # noqa: F401
        from .infrastructure.tasks import comprobar_presupuestos_task  # noqa: F401
