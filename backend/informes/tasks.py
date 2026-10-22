# informes/tasks.py — la ruta de siempre de la tarea de django.tasks (módulo 88). Vive en infrastructure/tasks/; la
# cola (django-tasks-db) la guarda por su ruta y el worker la busca aquí (core/infrastructure/tasks/ruta_estable.py).
from informes.infrastructure.tasks.enviar_informe_task import enviar_informe

__all__ = ["enviar_informe"]
