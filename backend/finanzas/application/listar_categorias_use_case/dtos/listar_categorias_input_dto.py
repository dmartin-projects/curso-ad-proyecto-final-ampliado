# finanzas/application/listar_categorias_use_case/dtos/listar_categorias_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarCategoriasInputDTO:
    hogar_id: int
    actor: Actor
    orden: tuple[str, ...] = ()
