# asistente/application/listar_graficos_fijados_use_case/dtos/listar_graficos_fijados_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarGraficosFijadosInputDTO:
    hogar_id: int
    actor: Actor
