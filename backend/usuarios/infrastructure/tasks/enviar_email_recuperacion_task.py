# usuarios/infrastructure/tasks/enviar_email_recuperacion_task.py — un email de la cuenta (django.tasks) (módulos 26, 35 y 88)
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.tasks import task
from django.utils import translation
from django.utils.translation import gettext as _

from core.infrastructure.tasks.ruta_estable import ruta_estable


@task(queue_name="emails")
@ruta_estable("usuarios.tasks")  # la ruta que guarda la cola (ruta_estable.py)
def enviar_email_recuperacion(usuario_id: int, enlace: str) -> None:
    usuario = get_user_model().objects.get(pk=usuario_id)
    with translation.override(usuario.idioma):
        send_mail(
            _("Recupera tu contraseña"),
            _("Abre este enlace para elegir una contraseña nueva: %(enlace)s") % {"enlace": enlace},
            None,
            [usuario.email],
        )
