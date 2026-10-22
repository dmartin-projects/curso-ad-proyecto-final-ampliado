# hogares/application/listar_miembros_use_case/dtos/listar_miembros_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarMiembrosInputDTO:
    hogar_id: int
    actor: Actor
    orden: tuple[str, ...] = ()
