# finanzas/application/eliminar_movimientos_use_case/dtos/eliminar_movimientos_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class EliminarMovimientosInputDTO:
    hogar_id: int
    actor: Actor
    ids: tuple[int, ...]
