# tickets/application/procesar_ticket_use_case/dtos/procesar_ticket_input_dto.py (módulos 74 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcesarTicketInputDTO:
    ticket_id: int
