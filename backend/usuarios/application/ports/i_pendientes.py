# usuarios/application/ports/i_pendientes.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.domain.vo.login_pendiente import LoginPendiente


class IPendientes(ABC):
    """Los inicios de sesión a medias (falta el segundo factor). Clave aleatoria → LoginPendiente, unos minutos."""

    @abstractmethod
    def guardar(self, pendiente: LoginPendiente) -> str: ...

    @abstractmethod
    def leer(self, clave: str) -> LoginPendiente | None: ...

    @abstractmethod
    def intento(self, clave: str) -> bool:
        """Anota un intento ANTES de comprobar el factor. False si ya no quedan (y se borra: vuelta a la contraseña)."""

    @abstractmethod
    def consumir(self, clave: str) -> LoginPendiente | None:
        """UNA vez: dos peticiones con el mismo segundo factor no abren dos sesiones."""
        ...
