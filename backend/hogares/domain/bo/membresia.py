# hogares/domain/bo/membresia.py — quién pertenece a un hogar y con qué rol (módulos 36, 71 y 88)
from dataclasses import dataclass
from typing import ClassVar

from core.domain.bo.i_auditable import IAuditable
from core.domain.enums.rol import Rol


@dataclass(eq=False)
class Membresia(IAuditable):
    tipo: ClassVar[str] = "hogares.membresia"  # para la auditoría (ejercicio 3 del módulo 88)

    hogar_id: int
    usuario_id: int
    rol: Rol = Rol.MIEMBRO
    id: int | None = None

    def __post_init__(self):
        self.rol = Rol(self.rol)

    def __str__(self) -> str:
        return f"Usuario {self.usuario_id} en el hogar {self.hogar_id} ({self.rol})"

    def datos_auditables(self) -> dict:
        return {"usuario_id": self.usuario_id, "rol": str(self.rol)}

    @property
    def es_admin(self) -> bool:
        return self.rol == Rol.ADMIN
