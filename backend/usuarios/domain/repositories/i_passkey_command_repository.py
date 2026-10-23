# usuarios/domain/repositories/i_passkey_command_repository.py — las passkeys de cada cuenta (módulo 92)
from abc import ABC, abstractmethod

from usuarios.domain.bo.passkey import Passkey


class IPasskeyCommandRepository(ABC):
    @abstractmethod
    def de_usuario(self, usuario_id: int) -> list[Passkey]: ...

    @abstractmethod
    def por_credencial(self, credencial_id: bytes) -> Passkey | None: ...

    @abstractmethod
    def guardar(self, passkey: Passkey) -> None:
        """Nueva (pone el id) o un uso (contador y sincronizada)."""

    @abstractmethod
    def borrar(self, usuario_id: int, passkey_id: int) -> str:
        """Devuelve su nombre. PasskeyNoEncontradaException si no es de ese usuario."""

    @abstractmethod
    def manija(self, usuario_id: int) -> bytes:
        """El user handle de WebAuthn: aleatorio y fijo por cuenta (ni el id ni el email: no identifica a nadie)."""

    @abstractmethod
    def usuario_de_manija(self, manija: bytes) -> int | None: ...
