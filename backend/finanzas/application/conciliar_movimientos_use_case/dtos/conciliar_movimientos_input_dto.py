# finanzas/application/conciliar_movimientos_use_case/dtos/conciliar_movimientos_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ConciliarMovimientosInputDTO:
    hogar_id: int
    actor: Actor
    huellas: dict[int, str]  # id del movimiento → huella de la fila del extracto
