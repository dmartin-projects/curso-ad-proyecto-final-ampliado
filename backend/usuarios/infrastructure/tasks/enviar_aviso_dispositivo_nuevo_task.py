# usuarios/infrastructure/tasks/enviar_aviso_dispositivo_nuevo_task.py — un email de la cuenta (django.tasks) (módulo 92)
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.tasks import task
from django.utils import formats, timezone, translation
from django.utils.translation import gettext as _

from core.infrastructure.tasks.ruta_estable import ruta_estable


@task(queue_name="emails")
@ruta_estable("usuarios.tasks")  # la ruta que guarda la cola (ruta_estable.py)
def enviar_aviso_dispositivo_nuevo(usuario_id: int, dispositivo: str, ip: str, momento: str) -> None:
    """Módulo 92: alguien ha entrado en la cuenta desde un navegador en el que nunca había entrado."""
    usuario = get_user_model().objects.get(pk=usuario_id)
    with translation.override(usuario.idioma), timezone.override(usuario.zona_horaria):
        cuando = formats.date_format(timezone.localtime(datetime.fromisoformat(momento)), "DATETIME_FORMAT")
        send_mail(
            _("Nuevo inicio de sesión en tu cuenta de Gastos"),
            _(
                "Se ha entrado en tu cuenta desde un dispositivo nuevo: %(dispositivo)s (red %(ip)s), el %(cuando)s.\n\n"
                "Si has sido tú, no tienes que hacer nada. Si no, cierra esa sesión en %(enlace)s, cambia tu "
                "contraseña y activa la verificación en dos pasos."
            )
            % {
                "dispositivo": dispositivo,
                "ip": ip or "?",
                "cuando": cuando,
                "enlace": f"{settings.FRONTEND_URL}/sesiones",
            },
            None,
            [usuario.email],
        )
