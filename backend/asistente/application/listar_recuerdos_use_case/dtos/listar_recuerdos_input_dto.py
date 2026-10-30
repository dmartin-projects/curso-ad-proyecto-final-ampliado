# asistente/application/listar_recuerdos_use_case/dtos/listar_recuerdos_input_dto.py (módulo 99)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarRecuerdosInputDTO:
    hogar_id: int
    actor: Actor
