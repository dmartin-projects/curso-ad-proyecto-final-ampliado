# core/domain/repositories/queries/listado_del_hogar_query.py — los listados cortos de un hogar (módulos 87 y 88)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListadoDelHogarQuery:
    """Listados cortos, sin paginar: todos los del hogar, en el orden pedido (vacío: el de siempre)."""

    hogar_id: int
    orden: tuple[str, ...] = ()
