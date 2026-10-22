# tickets/application/obtener_ticket_use_case/dtos/obtener_ticket_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerTicketInputDTO:
    hogar_id: int
    actor: Actor
    ticket_id: int
