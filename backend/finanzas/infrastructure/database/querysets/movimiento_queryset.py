# finanzas/infrastructure/database/querysets/movimiento_queryset.py — las consultas reutilizables del ORM
# (módulos 07, 72 y 87)
from datetime import date

from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from core.domain.vo.mes import Mes


class MovimientoQuerySet(models.QuerySet):
    def del_hogar(self, hogar):
        return self.filter(hogar=hogar)

    def visibles_para(self, usuario):
        return self.filter(hogar__membresias__usuario=usuario)

    def gastos(self):
        return self.filter(importe__lt=0)

    def ingresos(self):
        return self.filter(importe__gt=0)

    def del_mes(self, mes: Mes | date):
        mes = mes if isinstance(mes, Mes) else Mes.de(mes)
        return self.filter(fecha__gte=mes.inicio, fecha__lt=mes.fin)  # rango: usa el índice (no __month)

    def pendientes_revision(self):
        return self.filter(revisado=False)

    def total(self):
        return self.aggregate(t=Coalesce(Sum("importe"), models.Value(0), output_field=models.DecimalField()))["t"]

    def con_detalle(self):
        return self.select_related("cuenta", "categoria", "categoria__padre", "comercio")

    def buscar(self, texto: str):
        return self.filter(
            Q(concepto__icontains=texto) | Q(comercio__nombre__icontains=texto) | Q(notas__icontains=texto)
        )
