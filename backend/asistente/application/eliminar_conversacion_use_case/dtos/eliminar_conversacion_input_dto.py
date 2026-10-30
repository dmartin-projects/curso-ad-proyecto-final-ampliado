# asistente/application/eliminar_conversacion_use_case/dtos/eliminar_conversacion_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class EliminarConversacionInputDTO:
    hogar_id: int
    actor: Actor
    conversacion_id: int
