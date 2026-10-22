# hogares/domain/repositories/queries/hogares_query.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True, slots=True)
class HogaresQuery:
    """Los hogares de una persona, en el orden pedido (vacío: por nombre)."""

    usuario_id: int
    orden: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
