# core/domain/repositories/queries/paginacion_cursor.py — paginación por cursor (módulo 87)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PaginacionCursor:
    """Listados largos con scroll infinito: rendimiento constante, sin contar la tabla. El cursor es opaco: lo
    genera el query service en `Pagina.siguiente`/`anterior` y solo él sabe leerlo (None: la primera página)."""

    cursor: str | None = None
    tamano: int = 50
