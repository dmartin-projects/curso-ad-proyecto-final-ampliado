# backoffice/domain/read_models/hogar_soporte.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from backoffice.domain.read_models.miembro_soporte import MiembroSoporte


@dataclass(frozen=True, slots=True)
class HogarSoporte:
    id: int
    nombre: str
    zona_horaria: str
    num_miembros: int
    num_movimientos: int
    creado: datetime
    miembros: tuple[MiembroSoporte, ...] = ()  # solo en el detalle
