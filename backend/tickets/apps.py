from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tickets"

    def ready(self):
        # Los adapters de entrada que Django y Celery no descubren solos (módulos 87 y 88)
        from .infrastructure.metrics import metricas_tickets
        from .infrastructure.tasks import procesar_ticket_task  # noqa: F401

        metricas_tickets.registrar()  # sin OpenTelemetry activo, el SDK nunca llama a la función
