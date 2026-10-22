# usuarios/application/ports/i_enlaces.py (módulo 88)
from abc import ABC, abstractmethod


class IEnlaces(ABC):
    """Enlaces de un solo uso hacia una página del frontend (completar el registro, elegir otra contraseña)."""

    @abstractmethod
    def crear(self, usuario_id: int, ruta: str) -> str: ...

    @abstractmethod
    def usuario_de(self, uid: str, token: str) -> int | None: ...
