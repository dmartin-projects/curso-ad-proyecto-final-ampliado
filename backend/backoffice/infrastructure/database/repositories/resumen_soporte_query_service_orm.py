# backoffice/infrastructure/database/repositories/resumen_soporte_query_service_orm.py — IResumenSoporteQueryService con el ORM (módulo 88)
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone

from backoffice.domain.read_models.por_estado import PorEstado
from backoffice.domain.read_models.resumen_soporte import ResumenSoporte
from backoffice.domain.repositories.i_resumen_soporte_query_service import IResumenSoporteQueryService
from hogares.models import Hogar as HogarModel
from importaciones.models import Importacion as ImportacionModel
from tickets.infrastructure.database.repositories.ticket_query_service_orm import TicketQueryServiceORM
from tickets.models import Ticket as TicketModel


class ResumenSoporteQueryServiceORM(IResumenSoporteQueryService):
    def resumen(self):
        ahora = timezone.now()
        por_estado = (
            TicketModel.objects.filter(creado__gte=ahora - timedelta(hours=24))
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )
        importaciones = ImportacionModel.objects.aggregate(
            en_curso=Count("id", filter=Q(estado__in=["pendiente", "analizando", "importando"])),
            con_error=Count("id", filter=Q(estado="error", creado__gte=ahora - timedelta(days=7))),
        )
        return ResumenSoporte(
            tickets_24h=tuple(PorEstado(f["estado"], f["total"]) for f in por_estado),
            # el mismo criterio que la métrica (módulo 84): el query service de tickets, que se puede compartir
            tickets_atascados=TicketQueryServiceORM().contar_atascados(),
            importaciones_en_curso=importaciones["en_curso"],
            importaciones_con_error_7d=importaciones["con_error"],
            hogares=HogarModel.objects.count(),
            usuarios_activos=get_user_model().objects.filter(is_active=True).count(),
        )
