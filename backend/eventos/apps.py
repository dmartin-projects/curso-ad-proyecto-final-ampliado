from django.apps import AppConfig


class EventosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventos"
    verbose_name = "Eventos (Kafka)"

    def ready(self):
        from . import receptores  # noqa: F401  (registra los receptores de señales)
