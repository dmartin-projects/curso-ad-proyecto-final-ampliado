# backoffice/application/obtener_ticket_soporte_use_case/dtos/obtener_ticket_soporte_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerTicketSoporteInputDTO:
    ticket_id: int
