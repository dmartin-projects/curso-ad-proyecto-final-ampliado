# importaciones/application/listar_importaciones_use_case/dtos/listar_importaciones_input_dto.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion
from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarImportacionesInputDTO:
    hogar_id: int
    actor: Actor
    estado: str | None = None
    cuenta_id: int | None = None
    orden: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
