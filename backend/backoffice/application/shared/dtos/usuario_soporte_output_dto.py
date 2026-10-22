# backoffice/application/shared/dtos/usuario_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from backoffice.domain.read_models.usuario_soporte import UsuarioSoporte


@dataclass(frozen=True, slots=True)
class UsuarioSoporteOutputDTO:
    id: int
    email: str
    nombre: str
    apellidos: str
    is_active: bool
    is_staff: bool
    fecha_alta: datetime
    last_login: datetime | None

    @classmethod
    def desde_read_model(cls, rm: UsuarioSoporte) -> "UsuarioSoporteOutputDTO":
        return cls(
            id=rm.id,
            email=rm.email,
            nombre=rm.nombre,
            apellidos=rm.apellidos,
            is_active=rm.is_active,
            is_staff=rm.is_staff,
            fecha_alta=rm.fecha_alta,
            last_login=rm.last_login,
        )
