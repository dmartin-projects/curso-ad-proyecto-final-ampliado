# finanzas/domain/read_models/movimiento_sin_conciliar.py — lo que leen las importaciones para conciliar (módulo 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MovimientoSinConciliar:
    """Un gasto de la cuenta sin fila del banco (apuntado a mano o de un ticket): puede ser el de una fila."""

    id: int
    fecha: date
    importe: Decimal
