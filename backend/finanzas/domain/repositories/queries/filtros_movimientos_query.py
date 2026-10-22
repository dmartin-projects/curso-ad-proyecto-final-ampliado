# finanzas/domain/repositories/queries/filtros_movimientos_query.py — qué movimientos se piden (módulos 34 y 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class FiltrosMovimientosQuery:
    """Los filtros del listado y del CSV. Vacío (None, ()) = sin ese filtro."""

    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    importe_min: Decimal | None = None
    importe_max: Decimal | None = None
    cuentas: tuple[int, ...] = ()
    categorias: tuple[int, ...] = ()  # una categoría principal incluye a sus subcategorías
    sin_categoria: bool | None = None
    tipo: str | None = None  # "gasto" | "ingreso"
    etiqueta: str | None = None
    origen: str | None = None
    revisado: bool | None = None
    busqueda: tuple[str, ...] = ()  # cada término, en el concepto, el comercio o las notas; todos a la vez
