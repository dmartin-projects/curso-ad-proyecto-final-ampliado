from django.apps import AppConfig


class HogaresConfig(AppConfig):
    name = "hogares"

    def ready(self):
        # Los adapters de entrada que Django no descubre solos (módulos 87 y 88): los receivers y la tarea
        from .infrastructure.signals import receivers  # noqa: F401
        from .infrastructure.tasks import enviar_invitacion_task  # noqa: F401
