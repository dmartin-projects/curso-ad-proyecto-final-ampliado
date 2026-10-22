# finanzas/application/modificar_movimiento_use_case/dtos/modificar_movimiento_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ModificarMovimientoInputDTO:
    hogar_id: int
    actor: Actor
    movimiento_id: int
    cambios: dict  # solo lo que cambia (PATCH): {"importe": Decimal("-11"), "categoria_id": 4…}
