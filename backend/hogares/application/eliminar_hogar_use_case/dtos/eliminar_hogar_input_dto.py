# hogares/application/eliminar_hogar_use_case/dtos/eliminar_hogar_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class EliminarHogarInputDTO:
    hogar_id: int
    actor: Actor
