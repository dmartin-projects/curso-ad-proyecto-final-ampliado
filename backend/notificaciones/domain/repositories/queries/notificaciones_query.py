# notificaciones/domain/repositories/queries/notificaciones_query.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion_cursor import PaginacionCursor


@dataclass(frozen=True, slots=True)
class NotificacionesQuery:
    usuario_id: int
    leida: bool | None = None
    tipo: str | None = None
    hogar_id: int | None = None
    paginacion: PaginacionCursor = field(default_factory=PaginacionCursor)
