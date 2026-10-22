# finanzas/application/reordenar_categorias_use_case/dtos/reordenar_categorias_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ReordenarCategoriasInputDTO:
    hogar_id: int
    actor: Actor
    ids: tuple[int, ...]
