# backoffice/domain/read_models/usuario_soporte.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class UsuarioSoporte:
    id: int
    email: str
    nombre: str
    apellidos: str
    is_active: bool
    is_staff: bool
    fecha_alta: datetime
    last_login: datetime | None
