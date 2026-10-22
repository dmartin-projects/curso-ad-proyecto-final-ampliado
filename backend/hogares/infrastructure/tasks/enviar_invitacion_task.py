# hogares/infrastructure/tasks/enviar_invitacion_task.py — el email de la invitación (django.tasks) (módulos 26, 71 y 88)
from django.conf import settings
from django.core.mail import send_mail
from django.tasks import task
from django.utils.translation import gettext as _

from core.infrastructure.tasks.ruta_estable import ruta_estable
from hogares.infrastructure.database.models.invitacion_model import Invitacion as InvitacionModel


# django.tasks guarda en la cola la RUTA de la función: ruta_estable() conserva la de siempre (hogares.tasks…)
# y hogares/tasks.py la reexporta para que se pueda importar (core/infrastructure/tasks/ruta_estable.py)
@task(queue_name="emails")
@ruta_estable("hogares.tasks")
def enviar_invitacion(invitacion_id: int) -> None:
    inv = InvitacionModel.objects.select_related("hogar", "invitado_por").get(pk=invitacion_id)
    enlace = f"{settings.FRONTEND_URL}/invitaciones/{inv.token}"
    send_mail(
        _("Te han invitado a «%(hogar)s»") % {"hogar": inv.hogar.nombre},
        _("%(quien)s te invita a compartir las cuentas de «%(hogar)s». Acepta aquí: %(enlace)s")
        % {
            "quien": inv.invitado_por.get_full_name() if inv.invitado_por else "",
            "hogar": inv.hogar.nombre,
            "enlace": enlace,
        },
        None,
        [inv.email],
    )
