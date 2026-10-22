# finanzas/application/desconciliar_movimientos_use_case/dtos/desconciliar_movimientos_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class DesconciliarMovimientosInputDTO:
    hogar_id: int
    actor: Actor
    ids: tuple[int, ...]
