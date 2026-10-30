# asistente/application/obtener_conversacion_use_case/dtos/obtener_conversacion_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerConversacionInputDTO:
    hogar_id: int
    actor: Actor
    conversacion_id: int
