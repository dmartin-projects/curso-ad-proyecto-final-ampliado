# usuarios/tasks.py — la ruta de siempre de las tareas de django.tasks (módulos 88, 91 y 92). Viven en infrastructure/tasks/;
# la cola (django-tasks-db) las guarda por su ruta y el worker las busca aquí (core/infrastructure/tasks/ruta_estable.py).
from usuarios.infrastructure.tasks.enviar_aviso_dispositivo_nuevo_task import enviar_aviso_dispositivo_nuevo
from usuarios.infrastructure.tasks.enviar_aviso_seguridad_task import enviar_aviso_seguridad
from usuarios.infrastructure.tasks.enviar_aviso_vinculacion_task import enviar_aviso_vinculacion
from usuarios.infrastructure.tasks.enviar_email_completar_registro_task import enviar_email_completar_registro
from usuarios.infrastructure.tasks.enviar_email_cuenta_existente_task import enviar_email_cuenta_existente
from usuarios.infrastructure.tasks.enviar_email_recuperacion_task import enviar_email_recuperacion

__all__ = [
    "enviar_aviso_dispositivo_nuevo",
    "enviar_aviso_seguridad",
    "enviar_aviso_vinculacion",
    "enviar_email_completar_registro",
    "enviar_email_cuenta_existente",
    "enviar_email_recuperacion",
]
