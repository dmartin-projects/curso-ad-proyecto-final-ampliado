# tickets/domain/vo/datos_ticket.py — lo que la IA ha leído de un ticket (módulos 74 y 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from tickets.domain.vo.linea import Linea


@dataclass(frozen=True)
class DatosTicket:
    """Lo que la IA ha leído del ticket, ya validado por su adapter (es una entrada externa más)."""

    comercio: str
    fecha: date | None
    total: Decimal | None  # positivo: lo pagado
    confianza: float
    nif: str = ""
    moneda: str = "EUR"
    categoria: str = ""  # el NOMBRE de una categoría del hogar que propone la IA ("" si ninguna encaja)
    lineas: tuple[Linea, ...] = ()
