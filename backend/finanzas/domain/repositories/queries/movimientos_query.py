# finanzas/domain/repositories/queries/movimientos_query.py (módulo 87)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion
from core.domain.repositories.queries.paginacion_cursor import PaginacionCursor
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery


@dataclass(frozen=True, slots=True)
class MovimientosQuery:
    hogar_id: int
    filtros: FiltrosMovimientosQuery = field(default_factory=FiltrosMovimientosQuery)
    orden: tuple[str, ...] = ()  # vacío: los más recientes primero; con orden, la paginación es por número
    paginacion: Paginacion | PaginacionCursor | None = None  # None: todos (el CSV)
