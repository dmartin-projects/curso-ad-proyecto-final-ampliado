# hogares/domain/bo/membresia.py — quién pertenece a un hogar y con qué rol (módulos 36, 71 y 88)
from dataclasses import dataclass

from core.domain.enums.rol import Rol


@dataclass(eq=False)
class Membresia:
    hogar_id: int
    usuario_id: int
    rol: Rol = Rol.MIEMBRO
    id: int | None = None

    def __post_init__(self):
        self.rol = Rol(self.rol)

    @property
    def es_admin(self) -> bool:
        return self.rol == Rol.ADMIN
