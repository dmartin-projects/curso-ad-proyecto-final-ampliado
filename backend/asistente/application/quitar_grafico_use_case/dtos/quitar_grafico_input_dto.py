# asistente/application/quitar_grafico_use_case/dtos/quitar_grafico_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class QuitarGraficoInputDTO:
    hogar_id: int
    actor: Actor
    grafico_id: int
