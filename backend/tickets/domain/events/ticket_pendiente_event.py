# tickets/domain/events/ticket_pendiente_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class TicketPendienteEvent:
    """Subido o reprocesado: hay que leerlo (OCR + IA) en segundo plano."""

    ticket_id: int
