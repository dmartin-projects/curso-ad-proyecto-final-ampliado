# core/domain/vo/actor.py — quién pide un use case y con qué rol (módulos 87 y 88)
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
    def sistema(cls, en_nombre_de: int | None = None) -> "Actor":
        """Procesos internos (crear las categorías de un hogar nuevo, tareas programadas).

        `en_nombre_de` (módulo 88): el proceso trabaja para alguien (el OCR del ticket que subió Ana, la importación
        que confirmó Luis). Lo que cree queda a su nombre (`creado_por`); el permiso se comprobó al pedirlo.
        """
        return cls(usuario_id=en_nombre_de, rol=Rol.ADMIN)

    @classmethod
    def soporte(cls, usuario_id: int) -> "Actor":
        """El personal de soporte en el backoffice (módulos 79 y 88). No es miembro del hogar: lo que puede hacer lo
        deciden los permisos de su grupo (los comprueba el backoffice); dentro del hogar actúa como un administrador
        y la auditoría lo apunta con su usuario."""
        return cls(usuario_id=usuario_id, rol=Rol.ADMIN)

    def exigir(self, minimo: Rol) -> None:
        if Rol(self.rol).nivel < minimo.nivel:
            raise SinPermisoException()
