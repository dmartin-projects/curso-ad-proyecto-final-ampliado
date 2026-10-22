# backoffice/application/shared/dtos/ticket_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from backoffice.domain.read_models.ticket_soporte import TicketSoporte


@dataclass(frozen=True, slots=True)
class TicketSoporteOutputDTO:
    id: int
    hogar_id: int
    hogar_nombre: str
    subido_por_email: str | None
    estado: str
    intentos: int
    confianza: Decimal | None
    error: str
    nombre_original: str
    creado: datetime
    actualizado: datetime

    @classmethod
    def desde_read_model(cls, rm: TicketSoporte) -> "TicketSoporteOutputDTO":
        return cls(
            id=rm.id,
            hogar_id=rm.hogar_id,
            hogar_nombre=rm.hogar_nombre,
            subido_por_email=rm.subido_por_email,
            estado=rm.estado,
            intentos=rm.intentos,
            confianza=rm.confianza,
            error=rm.error,
            nombre_original=rm.nombre_original,
            creado=rm.creado,
            actualizado=rm.actualizado,
        )
