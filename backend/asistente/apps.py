from django.apps import AppConfig


class AsistenteConfig(AppConfig):
    name = "asistente"
    verbose_name = "Asistente (agente de IA)"

    def ready(self):
        # Ejercicio 2 del módulo 98: un adapter de entrada que Django no descubre solo
        from .infrastructure.metrics import metricas_asistente

        metricas_asistente.registrar()  # sin OpenTelemetry activo, el SDK nunca llama a la función
