# hogares/application/listar_hogares_use_case/dtos/listar_hogares_input_dto.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True)
class ListarHogaresInputDTO:
    usuario_id: int
    orden: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
