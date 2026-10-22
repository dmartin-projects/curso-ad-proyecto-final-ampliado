from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        from .infrastructure.database.grupos import crear_grupos
        from .infrastructure.tasks import limpiar_resultados_de_tareas_task  # noqa: F401 (Celery solo busca core.tasks)

        # Una data migration no sirve: en una BD nueva los permisos se crean DESPUÉS de las migraciones
        post_migrate.connect(crear_grupos, sender=self, dispatch_uid="core_crear_grupos")

        # OpenTelemetry (módulo 84). Aquí y no en asgi.py: ready() se ejecuta en TODOS los procesos que
        # cargan Django (la web, los workers de Celery, Beat, db_worker, manage.py) y ANTES de que la web
        # cargue sus middlewares, que es cuando la instrumentación de Django tiene que estar puesta.
        # Sin OTEL_ENABLED=true no hace nada. Cada servicio se nombra con OTEL_SERVICE_NAME (compose).
        from .infrastructure.telemetry.telemetria import configurar

        configurar("gastos")
