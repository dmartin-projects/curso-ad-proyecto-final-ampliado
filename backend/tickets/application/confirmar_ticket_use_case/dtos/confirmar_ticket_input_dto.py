# tickets/application/confirmar_ticket_use_case/dtos/confirmar_ticket_input_dto.py (módulos 74 y 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ConfirmarTicketInputDTO:
    hogar_id: int
    actor: Actor
    ticket_id: int
    fecha: date
    total: Decimal
    concepto: str
    categoria_id: int | None = None
