# tickets/domain/repositories/queries/tickets_query.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True, slots=True)
class TicketsQuery:
    hogar_id: int
    estado: str | None = None
    cuenta_id: int | None = None
    busqueda: tuple[str, ...] = ()  # cada término, en el nombre del archivo o en el texto del OCR; todos a la vez
    orden: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
