# tickets/domain/events/ticket_borrado_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class TicketBorradoEvent:
    archivo: str  # el archivo se borra del almacén cuando se confirma la transacción
