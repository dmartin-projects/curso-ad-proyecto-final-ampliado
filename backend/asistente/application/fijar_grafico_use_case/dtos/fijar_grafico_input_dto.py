# asistente/application/fijar_grafico_use_case/dtos/fijar_grafico_input_dto.py (módulo 97)
from dataclasses import dataclass, field

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class FijarGraficoInputDTO:
    hogar_id: int
    actor: Actor
    especificacion: dict = field(default_factory=dict)
