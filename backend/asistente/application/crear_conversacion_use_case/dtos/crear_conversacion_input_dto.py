# asistente/application/crear_conversacion_use_case/dtos/crear_conversacion_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class CrearConversacionInputDTO:
    hogar_id: int
    actor: Actor
    carpeta_id: int | None = None
