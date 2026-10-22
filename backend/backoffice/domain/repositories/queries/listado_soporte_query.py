# backoffice/domain/repositories/queries/listado_soporte_query.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True, slots=True)
class ListadoSoporteQuery:
    """Un listado del backoffice: de TODOS los hogares, con los filtros ya validados por el adapter de entrada."""

    filtros: dict = field(default_factory=dict)  # campo del read model → valor (solo los que vienen)
    busqueda: tuple[str, ...] = ()
    orden: tuple[str, ...] = ()
    paginacion: Paginacion = field(default_factory=Paginacion)
