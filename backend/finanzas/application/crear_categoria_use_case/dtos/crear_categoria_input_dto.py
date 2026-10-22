# finanzas/application/crear_categoria_use_case/dtos/crear_categoria_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class CrearCategoriaInputDTO:
    hogar_id: int
    actor: Actor
    nombre: str
    padre_id: int | None = None
    color: str = "#607d8b"
    icono: str = ""
    orden: int = 0
    es_ingreso: bool = False
