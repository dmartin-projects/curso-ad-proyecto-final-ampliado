# finanzas/application/recategorizar_movimientos_use_case/dtos/recategorizar_movimientos_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class RecategorizarMovimientosInputDTO:
    hogar_id: int
    actor: Actor
    ids: tuple[int, ...]
    categoria_id: int
