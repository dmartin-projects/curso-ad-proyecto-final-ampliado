# finanzas/application/obtener_movimiento_use_case/dtos/obtener_movimiento_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerMovimientoInputDTO:
    hogar_id: int
    actor: Actor
    movimiento_id: int
