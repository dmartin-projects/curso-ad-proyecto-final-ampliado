from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tickets"

    def ready(self):
        from . import metricas

        metricas.registrar()  # sin OpenTelemetry activo, el SDK nunca llama a la función
