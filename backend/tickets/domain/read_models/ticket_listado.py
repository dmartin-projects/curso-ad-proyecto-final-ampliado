# tickets/domain/read_models/ticket_listado.py — un ticket con sus líneas y su gasto, para leerlo (módulo 88)
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class LineaListada:
    orden: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    importe: Decimal


@dataclass(frozen=True, slots=True)
class GastoDelTicket:
    """El movimiento que creó el ticket, con lo que enseña la pantalla del ticket."""

    id: int
    fecha: date
    importe: Decimal
    concepto: str
    categoria_id: int | None
    revisado: bool


@dataclass(frozen=True, slots=True)
class TicketListado:
    id: int
    estado: str
    cuenta_id: int
    nombre_original: str
    tipo: str
    archivo: str
    confianza: Decimal | None
    error: str
    datos_ia: dict
    intentos: int
    lineas: tuple[LineaListada, ...]
    gasto: GastoDelTicket | None
    creado: datetime
    procesado_en: datetime | None
