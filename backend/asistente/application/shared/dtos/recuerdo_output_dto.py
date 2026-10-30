# asistente/application/shared/dtos/recuerdo_output_dto.py (módulo 99)
from dataclasses import dataclass
from datetime import datetime

from asistente.domain.read_models.recuerdo_listado import RecuerdoListado


@dataclass(frozen=True, slots=True)
class RecuerdoOutputDTO:
    id: int
    texto: str
    creado: datetime

    @classmethod
    def desde_read_model(cls, r: RecuerdoListado) -> "RecuerdoOutputDTO":
        return cls(r.id, r.texto, r.creado)
