# asistente/application/asignar_plan_use_case/dtos/asignar_plan_input_dto.py (módulo 98)
from dataclasses import dataclass

from asistente.domain.enums.plan import Plan


@dataclass(frozen=True)
class AsignarPlanInputDTO:
    hogar_id: int
    plan: Plan
