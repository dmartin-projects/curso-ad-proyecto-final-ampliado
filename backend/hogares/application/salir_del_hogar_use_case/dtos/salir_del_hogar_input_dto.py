# hogares/application/salir_del_hogar_use_case/dtos/salir_del_hogar_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class SalirDelHogarInputDTO:
    hogar_id: int
    actor: Actor  # quien sale: su propia membresía
