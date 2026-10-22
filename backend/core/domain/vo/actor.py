# core/domain/vo/actor.py — quién pide un use case y con qué rol (módulo 87)
from dataclasses import dataclass

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException


@dataclass(frozen=True, slots=True)
class Actor:
    """Quien pide un use case: el usuario y su rol EN EL HOGAR de la operación.

    Lo construye el adaptador de entrada (la view, desde la membresía que ya ha resuelto; una tarea o un
    comando, como el sistema). El use case no sabe de requests ni de JWT: solo de actores.
    """

    usuario_id: int | None
    rol: Rol

    @classmethod
    def sistema(cls) -> "Actor":
        """Procesos internos (crear las categorías de un hogar nuevo, tareas programadas): sin usuario."""
        return cls(usuario_id=None, rol=Rol.ADMIN)

    def exigir(self, minimo: Rol) -> None:
        if Rol(self.rol).nivel < minimo.nivel:
            raise SinPermisoException()
