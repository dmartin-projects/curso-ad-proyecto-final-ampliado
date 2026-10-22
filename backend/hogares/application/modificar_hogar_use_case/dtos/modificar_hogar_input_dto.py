# hogares/application/modificar_hogar_use_case/dtos/modificar_hogar_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ModificarHogarInputDTO:
    hogar_id: int
    actor: Actor
    cambios: dict  # nombre, moneda, zona_horaria
