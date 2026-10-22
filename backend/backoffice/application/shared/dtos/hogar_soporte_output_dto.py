# backoffice/application/shared/dtos/hogar_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from backoffice.application.shared.dtos.miembro_soporte_output_dto import MiembroSoporteOutputDTO
from backoffice.domain.read_models.hogar_soporte import HogarSoporte


@dataclass(frozen=True, slots=True)
class HogarSoporteOutputDTO:
    id: int
    nombre: str
    zona_horaria: str
    num_miembros: int
    num_movimientos: int
    creado: datetime
    miembros: tuple[MiembroSoporteOutputDTO, ...] = ()  # solo en el detalle

    @classmethod
    def desde_read_model(cls, rm: HogarSoporte) -> "HogarSoporteOutputDTO":
        return cls(
            id=rm.id,
            nombre=rm.nombre,
            zona_horaria=rm.zona_horaria,
            num_miembros=rm.num_miembros,
            num_movimientos=rm.num_movimientos,
            creado=rm.creado,
            miembros=tuple(MiembroSoporteOutputDTO.desde_read_model(x) for x in rm.miembros),
        )
