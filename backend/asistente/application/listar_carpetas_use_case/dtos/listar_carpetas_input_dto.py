# asistente/application/listar_carpetas_use_case/dtos/listar_carpetas_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarCarpetasInputDTO:
    hogar_id: int
    actor: Actor
