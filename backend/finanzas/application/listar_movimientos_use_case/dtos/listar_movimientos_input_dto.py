# finanzas/application/listar_movimientos_use_case/dtos/listar_movimientos_input_dto.py (módulo 87)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion
from core.domain.repositories.queries.paginacion_cursor import PaginacionCursor
from core.domain.vo.actor import Actor
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery


@dataclass(frozen=True)
class ListarMovimientosInputDTO:
    hogar_id: int
    actor: Actor
    filtros: FiltrosMovimientosQuery = field(default_factory=FiltrosMovimientosQuery)
    orden: tuple[str, ...] = ()
    paginacion: Paginacion | PaginacionCursor = field(default_factory=PaginacionCursor)
