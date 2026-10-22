# finanzas/infrastructure/api/v1/views/consultas.py — los query params de un listado, traducidos (módulo 87)
#
# Las mismas piezas de DRF que filtraban el QuerySet (OrderingFilter, SearchFilter, django-filter) se usan aquí solo
# para LEER y VALIDAR los parámetros, con los mismos errores de siempre; filtrar es cosa del query service.
from django.http import Http404
from django.utils.translation import gettext as _
from django_filters.utils import translate_validation
from rest_framework.filters import OrderingFilter, SearchFilter


def orden(view, request, modelo) -> tuple[str, ...]:
    """?ordering=… con los campos que la view permite; sin él (o si ninguno vale), el `ordering` de la view."""
    return tuple(OrderingFilter().get_ordering(request, modelo.objects.none(), view) or ())


def busqueda(request) -> tuple[str, ...]:
    """?search=… partido en términos, como SearchFilter."""
    return tuple(SearchFilter().get_search_terms(request))


def filtros(clase_filterset, request, modelo):
    """El FilterSet validado (400 con los errores de siempre si algo no vale)."""
    filtro = clase_filterset(data=request.query_params, queryset=modelo.objects.none(), request=request)
    if not filtro.is_valid():
        raise translate_validation(filtro.errors)
    return filtro


def id_de_la_url(view) -> int:
    """El id de /…/{id}/. Si no es un número, 404, como get_object()."""
    try:
        return int(view.kwargs[view.lookup_url_kwarg or view.lookup_field])
    except (TypeError, ValueError):
        raise Http404 from None


def no_encontrado(modelo) -> Http404:
    """El mismo 404 que get_object() cuando no hay fila: un use case de consulta devuelve None, la view traduce."""
    return Http404(_("No %s matches the given query.") % modelo._meta.object_name)
