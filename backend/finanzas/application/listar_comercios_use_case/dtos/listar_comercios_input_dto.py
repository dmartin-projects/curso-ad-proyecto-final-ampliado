# finanzas/application/listar_comercios_use_case/dtos/listar_comercios_input_dto.py (módulo 87)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True)
class ListarComerciosInputDTO:
    busqueda: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
