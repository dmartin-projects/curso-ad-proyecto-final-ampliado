from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notificaciones"

    def ready(self):
        # Los adapters de entrada que Django y Celery no descubren solos (módulos 15, 87 y 88)
        from .infrastructure.signals import receivers  # noqa: F401
        from .infrastructure.tasks import emitir_evento_hogar_task, enviar_email_notificacion_task  # noqa: F401
