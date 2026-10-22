# hogares/tasks.py — la ruta de siempre de la tarea de django.tasks (módulo 88). Vive en infrastructure/tasks/; la
# cola (django-tasks-db) la guarda por su ruta y el worker la busca aquí (core/infrastructure/tasks/ruta_estable.py).
from hogares.infrastructure.tasks.enviar_invitacion_task import enviar_invitacion

__all__ = ["enviar_invitacion"]
