from django.apps import AppConfig


class EventosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventos"
    verbose_name = "Eventos (Kafka)"

    def ready(self):
        # Los adapters de entrada que Django y Celery no descubren solos (módulos 87 y 88): los receivers (se
        # conectan al importarse), la tarea (Celery solo busca <app>.tasks) y las métricas del outbox
        from .infrastructure.metrics import metricas_outbox
        from .infrastructure.signals import receivers  # noqa: F401
        from .infrastructure.tasks import limpiar_eventos_publicados_task  # noqa: F401

        metricas_outbox.registrar()  # ejercicio 1 del 85: sin OpenTelemetry activo, el SDK nunca llama a los callbacks
