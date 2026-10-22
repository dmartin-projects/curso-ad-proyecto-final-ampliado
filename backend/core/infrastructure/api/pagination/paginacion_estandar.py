# core/infrastructure/api/pagination/paginacion_estandar.py — la paginación por defecto de la API (módulos 37 y 87)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

from core.domain.read_models.pagina import Pagina
from core.domain.repositories.queries.paginacion import Paginacion


class PaginacionEstandar(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"  # ?page_size=50
    max_page_size = 100  # 🔐 sin máximo, ?page_size=1000000

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):  # para que OpenAPI documente la forma (módulo 38)
        base = super().get_paginated_response_schema(schema)
        base["properties"].update(
            {
                "total_pages": {"type": "integer"},
                "page": {"type": "integer"},
                "page_size": {"type": "integer"},
            }
        )
        return base

    # ── La misma respuesta, a partir de la Pagina que devuelve un use case de consulta (módulo 87) ──
    def paginacion(self, request) -> Paginacion:
        """?page=…&page_size=… → la Paginacion del dominio (el tamaño, con el máximo de siempre)."""
        numero = request.query_params.get(self.page_query_param) or "1"
        return Paginacion(numero=numero, tamano=self.get_page_size(request), ultima=numero in self.last_page_strings)

    def respuesta(self, request, pagina: Pagina, datos) -> Response:
        url = request.build_absolute_uri()
        siguiente = replace_query_param(url, self.page_query_param, pagina.siguiente) if pagina.siguiente else None
        anterior = None
        if pagina.anterior == "1":
            anterior = remove_query_param(url, self.page_query_param)
        elif pagina.anterior:
            anterior = replace_query_param(url, self.page_query_param, pagina.anterior)
        return Response(
            {
                "count": pagina.count,
                "total_pages": pagina.total_paginas,
                "page": pagina.numero,
                "page_size": pagina.tamano,
                "next": siguiente,
                "previous": anterior,
                "results": datos,
            }
        )
