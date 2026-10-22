# finanzas/application/modificar_presupuesto_use_case/dtos/modificar_presupuesto_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ModificarPresupuestoInputDTO:
    hogar_id: int
    actor: Actor
    presupuesto_id: int
    cambios: dict  # categoria_id, mes (date), importe (Decimal)
