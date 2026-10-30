# asistente/application/modificar_conversacion_use_case/dtos/modificar_conversacion_input_dto.py (módulo 97)
from dataclasses import dataclass, field

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ModificarConversacionInputDTO:
    hogar_id: int
    actor: Actor
    conversacion_id: int
    cambios: dict = field(default_factory=dict)
