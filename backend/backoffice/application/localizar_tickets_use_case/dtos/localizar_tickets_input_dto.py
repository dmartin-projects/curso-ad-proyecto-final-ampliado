# backoffice/application/localizar_tickets_use_case/dtos/localizar_tickets_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class LocalizarTicketsInputDTO:
    ids: tuple[int, ...]
