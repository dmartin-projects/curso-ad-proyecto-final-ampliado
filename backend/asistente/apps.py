from django.apps import AppConfig


class AsistenteConfig(AppConfig):
    name = "asistente"
    verbose_name = "Asistente (agente de IA)"

    def ready(self):
        # Los adapters de entrada que Django y Celery no descubren solos (módulos 98 y 99)
        from .infrastructure.metrics import metricas_asistente
        from .infrastructure.tasks import (
            analizar_mes_task,  # noqa: F401 (módulo 105)
            compactar_conversacion_task,  # noqa: F401 (módulo 99)
        )

        metricas_asistente.registrar()  # sin OpenTelemetry activo, el SDK nunca llama a la función
