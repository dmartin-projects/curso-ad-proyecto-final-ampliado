# finanzas/application/listar_presupuestos_use_case/dtos/listar_presupuestos_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class ListarPresupuestosInputDTO:
    hogar_id: int
    actor: Actor
    mes: Mes | None = None
    orden: tuple[str, ...] = ()
