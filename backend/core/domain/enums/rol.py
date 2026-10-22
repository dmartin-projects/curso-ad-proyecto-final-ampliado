# core/domain/enums/rol.py — los roles de una membresía (módulos 36 y 87)
from enum import StrEnum


class Rol(StrEnum):
    """Los roles de una membresía (módulo 36). Mismos valores que Membresia.Rol: se convierten sin tabla."""

    LECTOR = "lector"
    MIEMBRO = "miembro"
    ADMIN = "admin"

    @property
    def nivel(self) -> int:
        return {"lector": 0, "miembro": 1, "admin": 2}[self.value]
