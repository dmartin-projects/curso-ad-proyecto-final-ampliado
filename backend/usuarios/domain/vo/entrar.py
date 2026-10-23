# usuarios/domain/vo/entrar.py — lo que se decide a la vuelta del proveedor: entrar en una cuenta (módulo 91)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entrar:
    usuario_id: int
