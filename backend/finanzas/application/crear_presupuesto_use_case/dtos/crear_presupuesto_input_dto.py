# finanzas/application/crear_presupuesto_use_case/dtos/crear_presupuesto_input_dto.py (módulo 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class CrearPresupuestoInputDTO:
    hogar_id: int
    actor: Actor
    categoria_id: int
    mes: date
    importe: Decimal
