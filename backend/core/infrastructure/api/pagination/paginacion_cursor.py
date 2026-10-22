# core/infrastructure/api/pagination/paginacion_cursor.py — listados largos con scroll infinito (módulos 37 y 87)
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from core.domain.read_models.pagina import Pagina
from core.domain.repositories.queries.paginacion_cursor import PaginacionCursor as PaginacionCursorQuery


class PaginacionCursor(CursorPagination):
    """Para listados largos con scroll infinito (movimientos): rendimiento constante y estable."""

    page_size = 50
    ordering = ("-fecha", "-id")

    # ── La misma respuesta, a partir de la Pagina que devuelve un use case de consulta (módulo 87) ──
    def paginacion(self, request) -> PaginacionCursorQuery:
        return PaginacionCursorQuery(cursor=request.query_params.get(self.cursor_query_param), tamano=self.page_size)

    def respuesta(self, request, pagina: Pagina, datos) -> Response:
        url = request.build_absolute_uri()
        return Response(
            {
                "next": replace_query_param(url, self.cursor_query_param, pagina.siguiente)
                if pagina.siguiente
                else None,
                "previous": replace_query_param(url, self.cursor_query_param, pagina.anterior)
                if pagina.anterior
                else None,
                "results": datos,
            }
        )
