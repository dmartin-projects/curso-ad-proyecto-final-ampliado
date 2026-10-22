# finanzas/application/exportar_movimientos_use_case/dtos/exportar_movimientos_input_dto.py (módulo 87)
from dataclasses import dataclass, field

from core.domain.vo.actor import Actor
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery


@dataclass(frozen=True)
class ExportarMovimientosInputDTO:
    hogar_id: int
    actor: Actor
    filtros: FiltrosMovimientosQuery = field(default_factory=FiltrosMovimientosQuery)
    orden: tuple[str, ...] = ()
