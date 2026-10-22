# informes/infrastructure/tasks/enviar_informe_task.py — el email del informe (django.tasks): un email por destinatario (módulos 26, 78 y 88)
from email.headerregistry import Address

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _

from core.domain.vo.mes import Mes
from core.infrastructure.tasks.ruta_estable import ruta_estable
from finanzas.domain.repositories.queries.dashboard_query import DashboardQuery
from finanzas.infrastructure.database.repositories.dashboard_query_service_orm import DashboardQueryServiceORM
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual as InformeMensualModel


# django.tasks guarda en la cola la RUTA de la función: ruta_estable() conserva la de siempre (informes.tasks…)
# y informes/tasks.py la reexporta para que se pueda importar (core/infrastructure/tasks/ruta_estable.py)
@task(queue_name="emails")  # django.tasks: un email por destinatario, con reintento independiente
@ruta_estable("informes.tasks")
def enviar_informe(informe_id: int, usuario_id: int) -> None:
    informe = InformeMensualModel.objects.select_related("hogar").get(pk=informe_id)
    usuario = get_user_model().objects.get(pk=usuario_id)
    with translation.override(usuario.idioma):
        contexto = {
            "usuario": usuario,
            "informe": informe,
            "resumen": DashboardQueryServiceORM().resumen(DashboardQuery(informe.hogar_id, Mes.de(informe.mes))),
            "enlace": f"/hogares/{informe.hogar_id}/informes",
            "frontend_url": settings.FRONTEND_URL,
        }
        mensaje = EmailMultiAlternatives(
            subject=_("Tu informe de %(mes)s · %(hogar)s")
            % {"mes": f"{informe.mes:%m/%Y}", "hogar": informe.hogar.nombre},
            body=render_to_string("informes/email_informe.txt", contexto),
            to=[Address(display_name=usuario.get_full_name(), addr_spec=usuario.email)],  # módulo 22
        )
        mensaje.attach_alternative(render_to_string("informes/email_informe.html", contexto), "text/html")
    with informe.archivo.open("rb") as f:
        mensaje.attach(f"gastos-{informe.mes:%Y-%m}.pdf", f.read(), "application/pdf")
    mensaje.send()
