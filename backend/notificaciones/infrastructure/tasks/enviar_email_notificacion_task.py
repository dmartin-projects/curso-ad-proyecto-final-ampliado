# notificaciones/infrastructure/tasks/enviar_email_notificacion_task.py — el email de una notificación (django.tasks) (módulos 26, 76 y 88)
from django.conf import settings
from django.core.mail import send_mail
from django.tasks import task
from django.utils import translation
from django.utils.translation import gettext as _

from core.infrastructure.tasks.ruta_estable import ruta_estable
from notificaciones.infrastructure.database.models.notificacion_model import Notificacion as NotificacionModel


# django.tasks guarda en la cola la RUTA de la función: ruta_estable() conserva la de siempre (notificaciones.tasks…)
# y notificaciones/tasks.py la reexporta para que se pueda importar (core/infrastructure/tasks/ruta_estable.py)
@task(queue_name="emails")  # django.tasks (módulo 26): un email sencillo no necesita Celery
@ruta_estable("notificaciones.tasks")
def enviar_email_notificacion(notificacion_id: int) -> None:
    n = NotificacionModel.objects.select_related("usuario").get(pk=notificacion_id)
    with translation.override(n.usuario.idioma):
        cuerpo = f"{n.mensaje}\n\n{_('Ábrelo en la app')}: {settings.FRONTEND_URL}{n.enlace}"
        send_mail(n.titulo, cuerpo, None, [n.usuario.email])
