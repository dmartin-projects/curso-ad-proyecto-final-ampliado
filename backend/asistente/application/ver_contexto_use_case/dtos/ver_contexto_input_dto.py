# asistente/application/ver_contexto_use_case/dtos/ver_contexto_input_dto.py (módulo 99, ejercicio 2)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class VerContextoInputDTO:
    hogar_id: int
    actor: Actor
    conversacion_id: int
    pregunta: str = "(la pregunta siguiente)"
