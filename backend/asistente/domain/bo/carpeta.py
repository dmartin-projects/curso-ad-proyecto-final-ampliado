# asistente/domain/bo/carpeta.py — para ordenar conversaciones ("Impuestos", "Viaje a Lisboa") (módulo 97)
from dataclasses import dataclass

from core.domain.exceptions.validacion_exception import ValidacionException

MAX_NOMBRE = 60


def comprobar_nombre(nombre: str) -> str:
    limpio = " ".join(nombre.split())
    if not limpio or len(limpio) > MAX_NOMBRE:
        raise ValidacionException(f"El nombre tiene entre 1 y {MAX_NOMBRE} caracteres.", campo="nombre")
    return limpio


@dataclass(eq=False)
class Carpeta:
    """De una persona en un hogar, como sus conversaciones. El nombre no se repite (lo garantiza el repositorio)."""

    usuario_id: int
    hogar_id: int
    nombre: str
    id: int | None = None

    def __post_init__(self):
        self.nombre = comprobar_nombre(self.nombre)
