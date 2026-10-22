# tickets/application/terminar_sin_gasto_use_case/dtos/terminar_sin_gasto_input_dto.py (módulos 74 y 88)
from dataclasses import dataclass

from tickets.domain.enums.estado_ticket import EstadoTicket


@dataclass(frozen=True)
class TerminarSinGastoInputDTO:
    ticket_id: int
    mensaje: str
    estado: EstadoTicket = EstadoTicket.ERROR
