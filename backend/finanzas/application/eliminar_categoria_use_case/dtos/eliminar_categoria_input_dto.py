# finanzas/application/eliminar_categoria_use_case/dtos/eliminar_categoria_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class EliminarCategoriaInputDTO:
    hogar_id: int
    actor: Actor
    categoria_id: int
