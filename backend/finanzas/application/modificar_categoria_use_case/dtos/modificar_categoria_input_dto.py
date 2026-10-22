# finanzas/application/modificar_categoria_use_case/dtos/modificar_categoria_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ModificarCategoriaInputDTO:
    hogar_id: int
    actor: Actor
    categoria_id: int
    cambios: dict  # nombre, color, icono, orden, es_ingreso y padre_id
