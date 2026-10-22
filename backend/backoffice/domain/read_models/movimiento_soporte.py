# backoffice/domain/read_models/movimiento_soporte.py (módulo 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MovimientoSoporte:
    id: int
    hogar_id: int
    fecha: date
    importe: Decimal
    concepto: str
    categoria_id: int | None
    categoria_nombre: str | None
    origen: str
    revisado: bool
