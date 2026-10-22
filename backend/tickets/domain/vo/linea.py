# tickets/domain/vo/linea.py — una línea de un ticket (módulos 74 y 88)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Linea:
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal

    @property
    def importe(self) -> Decimal:
        return self.cantidad * self.precio_unitario
