# tickets/domain/events/ticket_terminado_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class TicketTerminadoEvent:
    """Procesado, a revisión o con error: las notificaciones avisan a quien lo subió (módulo 76)."""

    ticket_id: int
