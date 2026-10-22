# importaciones/application/listar_filas_importacion_use_case/dtos/listar_filas_importacion_input_dto.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion
from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarFilasImportacionInputDTO:
    hogar_id: int
    actor: Actor
    importacion_id: int
    accion: str | None = None
    paginacion: Paginacion = field(default_factory=Paginacion)
