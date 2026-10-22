# tickets/application/subir_ticket_use_case/dtos/subir_ticket_input_dto.py (módulos 74 y 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class SubirTicketInputDTO:
    hogar_id: int
    actor: Actor
    cuenta_id: int
    contenido: object  # el archivo tal cual lo da el adapter de entrada: el use case no lo abre
    nombre_original: str
    tipo_archivo: str
    huella_archivo: str
