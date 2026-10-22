# finanzas/infrastructure/database/querysets/presupuesto_queryset.py (módulos 07, 76 y 87)
from django.db import models
from django.db.models import DateField, DecimalField, Func, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce


class MesSiguiente(Func):
    """`mes + 1 mes` calculado en PostgreSQL, para filtrar por RANGO dentro de una Subquery."""

    template = "(%(expressions)s + interval '1 month')::date"
    output_field = DateField()


class PresupuestoQuerySet(models.QuerySet):
    def con_gastado(self):
        """Anota `gastado`: lo gastado (negativo) en el mes del presupuesto, en su categoría y subcategorías.

        Una Subquery correlacionada (módulo 07): una sola consulta para todos los presupuestos.
        """
        from finanzas.infrastructure.database.models.movimiento_model import Movimiento  # se importan entre sí

        gastado = (
            Movimiento.objects.gastos()
            .filter(hogar=OuterRef("hogar"))
            .filter(Q(categoria=OuterRef("categoria")) | Q(categoria__padre=OuterRef("categoria")))
            # Rango, no TruncMonth("fecha") = mes: una función sobre la columna impide usar el índice y
            # PostgreSQL leería TODOS los movimientos del hogar por cada presupuesto (medido en el módulo 77)
            .filter(fecha__gte=OuterRef("mes"), fecha__lt=MesSiguiente(OuterRef("mes")))
            .values("hogar")
            .annotate(t=Sum("importe"))
            .values("t")
        )
        return self.annotate(gastado=Coalesce(Subquery(gastado), Value(0), output_field=DecimalField()))
