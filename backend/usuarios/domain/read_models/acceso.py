# usuarios/domain/read_models/acceso.py — las formas de entrar de una cuenta (módulos 91 y 92)
from dataclasses import dataclass

from usuarios.domain.read_models.identidad_vinculada import IdentidadVinculada


@dataclass(frozen=True, slots=True)
class Acceso:
    contrasena: bool
    identidades: tuple[IdentidadVinculada, ...] = ()
    passkeys: int = 0  # módulo 92: también son formas de entrar
