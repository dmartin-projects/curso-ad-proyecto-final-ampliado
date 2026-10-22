# backoffice/infrastructure/api/v1/views/listado_soporte_mixin.py — lo que comparten los listados de soporte (módulos 79 y 88)
from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery
from core.infrastructure.api.views import consultas


class ListadoSoporteMixin:
    # Los query params de un listado de soporte (filtros, ?search, ?ordering, ?page), validados con las piezas de
    # siempre (django-filter, SearchFilter, OrderingFilter), traducidos a la consulta del use case. Sin docstring: el
    # de una clase base acabaría en la descripción OpenAPI de cada vista.

    modelo = None  # el modelo del que salen el esquema OpenAPI y la validación de los filtros
    filtros_a_campos: dict[str, str] = {}  # filtro de la URL → campo del read model, cuando no se llaman igual

    def get_queryset(self):
        return self.modelo.objects.none()

    def _query(self, request) -> ListadoSoporteQuery:
        filtros = {}
        if getattr(self, "filterset_fields", None):
            datos = consultas.filtros(consultas.filterset_de_la_view(self, self.modelo), request, self.modelo)
            for nombre, valor in datos.form.cleaned_data.items():
                if valor is None or valor == "":
                    continue
                filtros[self.filtros_a_campos.get(nombre, nombre)] = getattr(valor, "pk", valor)
        return ListadoSoporteQuery(
            filtros=filtros,
            busqueda=consultas.busqueda(request),
            orden=consultas.orden(self, request, self.modelo),
            paginacion=self.paginator.paginacion(request),
        )

    def _pagina(self, request, pagina, presentar):
        datos = self.get_serializer([presentar(x) for x in pagina.results], many=True).data
        return self.paginator.respuesta(request, pagina, datos)

    def _o_404(self, leido):
        if leido is None:
            raise consultas.no_encontrado(self.modelo)
        return leido
