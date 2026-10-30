# asistente/application/shared/dtos/carpeta_output_dto.py (módulo 97)
from dataclasses import dataclass

from asistente.domain.bo.carpeta import Carpeta
from asistente.domain.read_models.carpeta_listada import CarpetaListada


@dataclass(frozen=True, slots=True)
class CarpetaOutputDTO:
    id: int
    nombre: str
    conversaciones: int = 0

    @classmethod
    def desde_bo(cls, c: Carpeta) -> "CarpetaOutputDTO":
        return cls(c.id, c.nombre)

    @classmethod
    def desde_read_model(cls, c: CarpetaListada) -> "CarpetaOutputDTO":
        return cls(c.id, c.nombre, c.conversaciones)
