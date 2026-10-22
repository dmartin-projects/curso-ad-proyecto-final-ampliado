# backoffice/domain/read_models/ticket_soporte.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class TicketSoporte:
    id: int
    hogar_id: int
    hogar_nombre: str
    subido_por_email: str | None
    estado: str
    intentos: int
    confianza: Decimal | None
    error: str
    nombre_original: str
    creado: datetime
    actualizado: datetime
