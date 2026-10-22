# tickets/application/shared/dtos/ticket_output_dto.py (módulo 88)
from dataclasses import dataclass

from tickets.domain.bo.ticket import Ticket


@dataclass(frozen=True, slots=True)
class TicketOutputDTO:
    id: int
    hogar_id: int
    cuenta_id: int
    estado: str
    subido_por_id: int | None
    archivo: str
    movimiento_id: int | None

    @classmethod
    def desde_bo(cls, t: Ticket) -> "TicketOutputDTO":
        return cls(
            id=t.id,
            hogar_id=t.hogar_id,
            cuenta_id=t.cuenta_id,
            estado=str(t.estado),
            subido_por_id=t.subido_por_id,
            archivo=t.archivo,
            movimiento_id=t.movimiento_id,
        )
