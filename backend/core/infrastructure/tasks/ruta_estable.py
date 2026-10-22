# core/infrastructure/tasks/ruta_estable.py — el "name=" que django.tasks no tiene (módulo 88)
#
# Celery guarda en cada mensaje el NOMBRE de la tarea, y se fija con name= al moverlas. django.tasks guarda la
# RUTA de la función ("hogares.tasks.enviar_invitacion") en la tabla de la cola (django-tasks-db) y el worker la
# importa con import_string(). Mover la función a infrastructure/tasks/ cambia esa ruta: las tareas ya encoladas
# no encontrarían su función, y las que encole la web nueva no las entendería un worker viejo.
#
# La solución tiene dos partes: la función conserva su ruta de siempre (este decorador) y <app>/tasks.py la
# reexporta, para que esa ruta se pueda importar.


def ruta_estable(modulo: str):
    """Pon @ruta_estable("<app>.tasks") DEBAJO de @task: la tarea se encola con la ruta de antes."""

    def decorar(funcion):
        funcion.__module__ = modulo
        return funcion

    return decorar
