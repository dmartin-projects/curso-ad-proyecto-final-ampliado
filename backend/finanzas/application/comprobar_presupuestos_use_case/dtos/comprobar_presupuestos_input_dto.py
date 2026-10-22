# finanzas/application/comprobar_presupuestos_use_case/dtos/comprobar_presupuestos_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class ComprobarPresupuestosInputDTO:
    hogar_id: int
    meses: tuple[Mes, ...]
