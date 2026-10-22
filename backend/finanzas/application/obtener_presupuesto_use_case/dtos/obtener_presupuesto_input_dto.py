# finanzas/application/obtener_presupuesto_use_case/dtos/obtener_presupuesto_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerPresupuestoInputDTO:
    hogar_id: int
    actor: Actor
    presupuesto_id: int
