# finanzas/domain/repositories/queries/comercios_query.py — el autocompletado de comercios (módulos 74 y 87)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True, slots=True)
class ComerciosQuery:
    busqueda: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
