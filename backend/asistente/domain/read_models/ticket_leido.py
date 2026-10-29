# asistente/domain/read_models/ticket_leido.py — un ticket, tal como lo leyó el OCR y la IA (módulo 95)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class TicketLeido:
    id: int
    estado: str
    comercio: str  # lo LEÍDO de una foto: texto de terceros, no fiable
    fecha: date | None
    total: Decimal | None
    lineas: tuple[str, ...]  # "2 × Leche 0,95", también leídas: no fiables
    gasto_id: int | None  # el movimiento que creó, si ya se confirmó
