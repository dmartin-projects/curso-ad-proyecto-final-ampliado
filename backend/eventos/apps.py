from django.apps import AppConfig


class EventosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventos"
    verbose_name = "Eventos (Kafka)"

    def ready(self):
        from . import metricas, receptores  # noqa: F401  (receptores: registra las señales)

        metricas.registrar()  # ejercicio 1: sin OpenTelemetry activo, el SDK nunca llama a los callbacks
