# asistente/application/confirmar_propuesta_use_case/dtos/confirmar_propuesta_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ConfirmarPropuestaInputDTO:
    hogar_id: int
    actor: Actor
    propuesta_id: int
