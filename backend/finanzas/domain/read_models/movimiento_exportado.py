# finanzas/domain/read_models/movimiento_exportado.py — una fila del CSV de movimientos (módulos 73 y 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MovimientoExportado:
    fecha: date
    concepto: str
    importe: Decimal
    cuenta: str
    categoria: str | None
    etiquetas: tuple[str, ...]
