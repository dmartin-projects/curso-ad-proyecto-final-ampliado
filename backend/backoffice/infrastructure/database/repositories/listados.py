# backoffice/infrastructure/database/repositories/listados.py — lo que comparten los listados de soporte (módulo 88)
from core.infrastructure.database import paginacion
from core.infrastructure.database.busqueda import buscar


def listar(qs, query, campos_busqueda: tuple[str, ...], a_read_model, *, filtros: dict | None = None):
    """Filtros (traducidos a los campos del modelo), búsqueda (como SearchFilter), orden y una página."""
    qs = qs.filter(**(filtros if filtros is not None else query.filtros))
    qs = buscar(qs, campos_busqueda, query.busqueda)
    if query.orden:
        qs = qs.order_by(*query.orden)
    return paginacion.por_numero(qs, query.paginacion, a_read_model)
