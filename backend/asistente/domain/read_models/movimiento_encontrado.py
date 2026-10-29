# asistente/domain/read_models/movimiento_encontrado.py (módulo 95)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MovimientoEncontrado:
    fecha: date
    importe: Decimal  # con signo: negativo, un gasto
    concepto: str
    categoria: str | None
    comercio: str | None
