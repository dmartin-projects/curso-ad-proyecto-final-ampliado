from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    name = "usuarios"

    def ready(self):
        # Las tareas de django.tasks se importan por su ruta (usuarios.tasks); aquí, como en el resto de apps, los
        # adapters de entrada que viven en infrastructure/ (módulos 87 y 88)
        from .infrastructure.api.schema import esquema_jwt  # noqa: F401  (módulo 92: el esquema de JWTConSesion)
        from .infrastructure.tasks import (  # noqa: F401
            enviar_aviso_dispositivo_nuevo_task,
            enviar_aviso_seguridad_task,
            enviar_aviso_vinculacion_task,
            enviar_email_completar_registro_task,
            enviar_email_cuenta_existente_task,
            enviar_email_recuperacion_task,
        )
