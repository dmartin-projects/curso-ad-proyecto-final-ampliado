# finanzas/application/crear_categorias_por_defecto_use_case/dtos/crear_categorias_por_defecto_input_dto.py (módulo 87)
from dataclasses import dataclass


@dataclass(frozen=True)
class CrearCategoriasPorDefectoInputDTO:
    hogar_id: int
