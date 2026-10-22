# backoffice/application/shared/dtos/por_estado_output_dto.py (módulo 88)
from dataclasses import dataclass

from backoffice.domain.read_models.por_estado import PorEstado


@dataclass(frozen=True, slots=True)
class PorEstadoOutputDTO:
    clave: str
    total: int

    @classmethod
    def desde_read_model(cls, rm: PorEstado) -> "PorEstadoOutputDTO":
        return cls(
            clave=rm.clave,
            total=rm.total,
        )
