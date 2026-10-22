# importaciones/domain/vo/candidato.py (módulos 75 y 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Candidato:
    """Un gasto de la cuenta sin fila del banco (apuntado a mano o de un ticket): puede ser el de una fila."""

    movimiento_id: int
    fecha: date
    importe: Decimal
