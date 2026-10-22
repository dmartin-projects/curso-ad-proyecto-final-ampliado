# importaciones/domain/read_models/fila_listada.py (módulo 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class FilaListada:
    """Una fila de la vista previa, con el concepto del gasto con el que se conciliará (si lo hay)."""

    id: int
    numero: int
    fecha: date
    concepto: str
    importe: Decimal
    accion: str
    coincide_con_id: int | None
    coincide_con_concepto: str | None
    movimiento_id: int | None
