# usuarios/application/ports/i_retos.py (módulo 92)
from abc import ABC, abstractmethod


class IRetos(ABC):
    """Los challenges de WebAuthn mientras el navegador habla con el autenticador: unos minutos y un solo uso."""

    @abstractmethod
    def guardar(self, ambito: str, challenge: bytes) -> None: ...

    @abstractmethod
    def consumir(self, ambito: str) -> bytes | None: ...
