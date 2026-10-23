# usuarios/infrastructure/tasks/enviar_aviso_vinculacion_task.py — un email de la cuenta (django.tasks) (módulo 91, ejercicio 2)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.tasks import task
from django.utils import translation
from django.utils.translation import gettext as _

from core.infrastructure.tasks.ruta_estable import ruta_estable


@task(queue_name="emails")
@ruta_estable("usuarios.tasks")  # la ruta que guarda la cola (ruta_estable.py)
def enviar_aviso_vinculacion(usuario_id: int, proveedor: str, cuenta: str) -> None:
    """Módulo 91, ejercicio 2: a su email de Gastos, que es el que seguro es suyo."""
    usuario = get_user_model().objects.get(pk=usuario_id)
    with translation.override(usuario.idioma):
        send_mail(
            _("Has vinculado %(proveedor)s a tu cuenta de Gastos") % {"proveedor": proveedor},
            _(
                "Desde ahora puedes entrar en Gastos con tu cuenta de %(proveedor)s (%(cuenta)s).\n\n"
                "Si no has sido tú, desvincúlala en %(enlace)s y cambia tu contraseña."
            )
            % {"proveedor": proveedor, "cuenta": cuenta, "enlace": f"{settings.FRONTEND_URL}/acceso"},
            None,
            [usuario.email],
        )
