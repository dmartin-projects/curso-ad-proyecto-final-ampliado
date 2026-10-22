# notificaciones/infrastructure/api/v1/views/paginacion_notificaciones.py (módulos 76 y 88)
from core.infrastructure.api.pagination.paginacion_cursor import PaginacionCursor


class PaginacionNotificaciones(PaginacionCursor):
    page_size = 20
    ordering = ("-creado", "-id")
