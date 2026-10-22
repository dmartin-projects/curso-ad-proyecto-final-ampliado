# importaciones/domain/bo/fila.py — una fila del extracto en el área de preparación (módulos 75 y 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from importaciones.domain.enums.accion import Accion


@dataclass
class Fila:
    """Una fila del extracto en el área de preparación (staging): lo leído, antes de crear nada."""

    numero: int
    fecha: date
    concepto: str
    importe: Decimal
    huella: str
    accion: Accion
    coincide_con_id: int | None = None  # el gasto que ya estaba y con el que se concilia
    movimiento_id: int | None = None  # el movimiento que acaba representando la fila (creado o conciliado)
    id: int | None = None
