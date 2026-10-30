# asistente/application/shared/dtos/propuesta_output_dto.py (módulo 97)
from dataclasses import dataclass
from typing import Any

from asistente.domain.bo.propuesta import Propuesta


@dataclass(frozen=True, slots=True)
class PropuestaOutputDTO:
    id: int
    tipo: str
    resumen: str
    estado: str
    resultado: dict[str, Any]

    @classmethod
    def desde_bo(cls, p: Propuesta) -> "PropuestaOutputDTO":
        return cls(p.id, str(p.tipo), p.resumen, str(p.estado), dict(p.resultado))
