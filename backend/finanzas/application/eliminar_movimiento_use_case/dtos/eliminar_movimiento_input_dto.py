# finanzas/application/eliminar_movimiento_use_case/dtos/eliminar_movimiento_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class EliminarMovimientoInputDTO:
    hogar_id: int
    actor: Actor
    movimiento_id: int
