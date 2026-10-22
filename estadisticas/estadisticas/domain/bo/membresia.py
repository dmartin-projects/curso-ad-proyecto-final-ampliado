# estadisticas/domain/bo/membresia.py — quién es miembro de qué hogar (módulos 85 y 89)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Membresia:
    """Quién es miembro de qué hogar: para decidir quién puede ver qué, sin preguntar a Django."""

    hogar_id: int
    usuario_id: int
    rol: str
    version: int
