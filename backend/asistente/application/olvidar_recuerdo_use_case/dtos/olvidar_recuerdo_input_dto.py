# asistente/application/olvidar_recuerdo_use_case/dtos/olvidar_recuerdo_input_dto.py (módulo 99)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class OlvidarRecuerdoInputDTO:
    hogar_id: int
    actor: Actor
    recuerdo_id: int
