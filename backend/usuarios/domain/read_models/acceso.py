# usuarios/domain/read_models/acceso.py — las formas de entrar de una cuenta (módulo 91)
from dataclasses import dataclass

from usuarios.domain.read_models.identidad_vinculada import IdentidadVinculada


@dataclass(frozen=True, slots=True)
class Acceso:
    contrasena: bool
    identidades: tuple[IdentidadVinculada, ...] = ()
