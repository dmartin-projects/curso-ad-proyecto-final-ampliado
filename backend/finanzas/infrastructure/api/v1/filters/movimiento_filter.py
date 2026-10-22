# finanzas/infrastructure/api/v1/filters/movimiento_filter.py — filtros del listado de movimientos (módulos 34 y 87)
#
# Valida los query params y documenta los filtros en OpenAPI; no filtra: a_dominio() los entrega como una
# FiltrosMovimientosQuery y el query service los aplica (con sus reglas: una categoría incluye a sus hijas).
import django_filters

from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from finanzas.infrastructure.database.models.cuenta_model import Cuenta as CuentaModel
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel


def _del_hogar(modelo):
    def queryset(request):
        vista = request.parser_context["view"] if request else None
        return modelo.objects.filter(hogar=vista.hogar) if vista and not vista.es_esquema() else modelo.objects.none()

    return queryset


class MovimientoFilter(django_filters.FilterSet):
    fecha = django_filters.DateFromToRangeFilter()  # ?fecha_after=&fecha_before=
    importe_min = django_filters.NumberFilter(field_name="importe", lookup_expr="gte")
    importe_max = django_filters.NumberFilter(field_name="importe", lookup_expr="lte")
    cuenta = django_filters.ModelMultipleChoiceFilter(queryset=_del_hogar(CuentaModel))
    categoria = django_filters.ModelMultipleChoiceFilter(queryset=_del_hogar(CategoriaModel))
    sin_categoria = django_filters.BooleanFilter(field_name="categoria", lookup_expr="isnull")
    tipo = django_filters.ChoiceFilter(choices=[("gasto", "Gastos"), ("ingreso", "Ingresos")])
    etiqueta = django_filters.CharFilter(field_name="etiquetas", lookup_expr="contains")

    class Meta:
        model = MovimientoModel
        fields = ["fecha", "cuenta", "categoria", "origen", "revisado"]

    # ── De los query params validados a la query del dominio (módulo 87) ──
    def a_dominio(self, busqueda: tuple[str, ...] = ()) -> FiltrosMovimientosQuery:
        """Como `serializer.a_dominio()`: django-filter valida y documenta en OpenAPI; el query service filtra."""
        d = self.form.cleaned_data
        fecha = d.get("fecha")  # un slice de datetimes (inicio y fin del día) o None
        return FiltrosMovimientosQuery(
            fecha_desde=fecha.start.date() if fecha and fecha.start else None,
            fecha_hasta=fecha.stop.date() if fecha and fecha.stop else None,
            importe_min=d.get("importe_min"),
            importe_max=d.get("importe_max"),
            cuentas=tuple(c.pk for c in d.get("cuenta") or ()),
            categorias=tuple(c.pk for c in d.get("categoria") or ()),
            sin_categoria=d.get("sin_categoria"),
            tipo=d.get("tipo") or None,
            etiqueta=d.get("etiqueta") or None,
            origen=d.get("origen") or None,
            revisado=d.get("revisado"),
            busqueda=busqueda,
        )
