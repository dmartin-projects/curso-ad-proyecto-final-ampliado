# tickets/application/reprocesar_ticket_use_case/dtos/reprocesar_ticket_input_dto.py (módulos 74 y 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ReprocesarTicketInputDTO:
    hogar_id: int
    actor: Actor
    ticket_id: int
    repetir_ocr: bool = False
