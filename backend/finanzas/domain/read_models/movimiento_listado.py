# finanzas/domain/read_models/movimiento_listado.py — un movimiento, tal como se lee (módulo 87)
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MovimientoListado:
    """Plano: con los nombres de su cuenta, su categoría y su comercio ya resueltos (una consulta, no N)."""

    id: int
    fecha: date
    importe: Decimal
    concepto: str
    cuenta_id: int
    cuenta_nombre: str
    categoria_id: int | None
    categoria_nombre: str | None
    categoria_color: str | None
    comercio_id: int | None
    comercio_nombre: str | None
    etiquetas: tuple[str, ...]
    notas: str
    origen: str
    revisado: bool
    num_adjuntos: int | None  # None: no se ha contado (el detalle no los cuenta; el listado, sí)
    creado: datetime
