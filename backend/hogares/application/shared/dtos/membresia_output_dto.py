# hogares/application/shared/dtos/membresia_output_dto.py (módulo 88)
from dataclasses import dataclass

from hogares.domain.bo.membresia import Membresia


@dataclass(frozen=True, slots=True)
class MembresiaOutputDTO:
    id: int
    hogar_id: int
    usuario_id: int
    rol: str

    @classmethod
    def desde_bo(cls, m: Membresia) -> "MembresiaOutputDTO":
        return cls(id=m.id, hogar_id=m.hogar_id, usuario_id=m.usuario_id, rol=str(m.rol))
