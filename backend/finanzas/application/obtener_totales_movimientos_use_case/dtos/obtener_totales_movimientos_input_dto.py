# finanzas/application/obtener_totales_movimientos_use_case/dtos/obtener_totales_movimientos_input_dto.py (módulo 95)
from dataclasses import dataclass, field

from core.domain.vo.actor import Actor
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery


@dataclass(frozen=True)
class ObtenerTotalesMovimientosInputDTO:
    hogar_id: int
    actor: Actor
    filtros: FiltrosMovimientosQuery = field(default_factory=FiltrosMovimientosQuery)
