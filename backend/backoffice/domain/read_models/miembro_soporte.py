# backoffice/domain/read_models/miembro_soporte.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MiembroSoporte:
    usuario_id: int
    email: str
    rol: str
