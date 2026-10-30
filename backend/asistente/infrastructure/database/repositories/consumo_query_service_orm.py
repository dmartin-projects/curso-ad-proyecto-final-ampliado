# asistente/infrastructure/database/repositories/consumo_query_service_orm.py (módulo 98)
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce

from asistente.domain.read_models.coste_por_hogar import CostePorHogar
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService
from asistente.infrastructure.database.models.consumo_model import Consumo as ConsumoModel

CERO = Decimal(0)


class ConsumoQueryServiceORM(IConsumoQueryService):
    def tokens(self, usuario_id, hogar_id, desde):
        filas = ConsumoModel.objects.filter(usuario_id=usuario_id, hogar_id=hogar_id, momento__gte=desde)
        return filas.aggregate(t=Coalesce(Sum(F("tokens_entrada") + F("tokens_salida")), 0))["t"]

    def coste(self, hogar_id, desde):
        filas = ConsumoModel.objects.filter(hogar_id=hogar_id, momento__gte=desde)
        return filas.aggregate(c=Coalesce(Sum("coste"), CERO))["c"]

    def por_hogar(self, desde, hasta, por_canal=False):
        campos = ["hogar_id", "hogar__nombre", "modelo", *(["canal"] if por_canal else [])]
        filas = (
            ConsumoModel.objects.filter(momento__gte=desde, momento__lt=hasta)
            .values(*campos)
            .annotate(
                llamadas=Count("id"),
                entrada=Sum("tokens_entrada"),
                cache=Sum("tokens_cache"),
                salida=Sum("tokens_salida"),
                coste_total=Coalesce(Sum("coste"), CERO),
                sin_precio=Count("id", filter=Q(coste__isnull=True)),
            )
            .order_by("-coste_total", "hogar_id", *campos[2:])
        )
        return tuple(
            CostePorHogar(
                hogar_id=f["hogar_id"],
                hogar=f["hogar__nombre"] or "(hogar borrado)",
                modelo=f["modelo"],
                llamadas=f["llamadas"],
                tokens_entrada=f["entrada"],
                tokens_cache=f["cache"],
                tokens_salida=f["salida"],
                coste=f["coste_total"],
                sin_precio=f["sin_precio"],
                canal=f.get("canal", ""),
            )
            for f in filas
        )

    def coste_por_hogar(self, desde):
        filas = (
            ConsumoModel.objects.filter(momento__gte=desde, hogar__isnull=False)
            .values("hogar_id")
            .annotate(c=Coalesce(Sum("coste"), CERO))
        )
        return {f["hogar_id"]: f["c"] for f in filas}
