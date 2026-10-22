# hogares/domain/read_models/miembro_listado.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MiembroListado:
    id: int  # la membresía
    usuario_id: int
    email: str
    nombre: str  # nombre y apellidos
    rol: str
    creado: datetime
