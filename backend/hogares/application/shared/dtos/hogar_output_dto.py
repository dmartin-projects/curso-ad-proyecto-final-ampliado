# hogares/application/shared/dtos/hogar_output_dto.py (módulo 88)
from dataclasses import dataclass

from hogares.domain.bo.hogar import Hogar


@dataclass(frozen=True, slots=True)
class HogarOutputDTO:
    id: int
    nombre: str
    moneda: str
    zona_horaria: str

    @classmethod
    def desde_bo(cls, h: Hogar) -> "HogarOutputDTO":
        return cls(id=h.id, nombre=h.nombre, moneda=h.moneda, zona_horaria=h.zona_horaria)
