# informes/infrastructure/pdf/maquetador_weasyprint.py — IMaquetador: plantilla de Django + WeasyPrint (módulos 78 y 88)
from datetime import date

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone, translation
from weasyprint import HTML

from core.domain.vo.mes import Mes
from finanzas.domain.repositories.queries.dashboard_query import DashboardQuery
from finanzas.infrastructure.database.repositories.dashboard_query_service_orm import DashboardQueryServiceORM
from finanzas.infrastructure.database.repositories.movimiento_query_service_orm import MovimientoQueryServiceORM
from hogares.models import Hogar
from informes.application.ports.i_maquetador import IMaquetador


def contexto(hogar: Hogar, mes: date) -> dict:
    return {
        "hogar": hogar,
        # los mismos números que el dashboard (módulo 77): el query service de finanzas, que se puede compartir
        "resumen": DashboardQueryServiceORM().resumen(DashboardQuery(hogar.pk, Mes.de(mes))),
        # {% regroup %} agrupa elementos CONSECUTIVOS: del_mes() los da ordenados por la categoría
        "movimientos": MovimientoQueryServiceORM().del_mes(hogar.pk, Mes.de(mes)),
        "generado": timezone.localtime(),
    }


def pdf(hogar: Hogar, mes: date, idioma: str | None = None) -> bytes:
    with translation.override(idioma or settings.LANGUAGE_CODE):
        html = render_to_string("informes/mensual.html", contexto(hogar, mes))
    return HTML(string=html).write_pdf()


class MaquetadorWeasyPrint(IMaquetador):
    def pdf(self, hogar_id: int, mes: Mes, idioma: str | None = None) -> bytes:
        return pdf(Hogar.objects.get(pk=hogar_id), mes.inicio, idioma)
