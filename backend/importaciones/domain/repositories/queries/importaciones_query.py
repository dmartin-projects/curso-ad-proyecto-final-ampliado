# importaciones/domain/repositories/queries/importaciones_query.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True, slots=True)
class ImportacionesQuery:
    hogar_id: int
    estado: str | None = None
    cuenta_id: int | None = None
    orden: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
