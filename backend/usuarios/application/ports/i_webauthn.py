# usuarios/application/ports/i_webauthn.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.domain.bo.passkey import Passkey
from usuarios.domain.vo.credencial_nueva import CredencialNueva
from usuarios.domain.vo.firma_comprobada import FirmaComprobada
from usuarios.domain.vo.reto import Reto


class IWebAuthn(ABC):
    """Las ceremonias de WebAuthn: las opciones para el navegador y la comprobación de su respuesta (firma, challenge,
    origen, rp_id, flags y contador). El rp_id y el origen son los del entorno."""

    @abstractmethod
    def opciones_de_registro(self, *, manija: bytes, cuenta: str, nombre: str, excluir: list[bytes]) -> Reto: ...

    @abstractmethod
    def comprobar_registro(self, respuesta: dict, challenge: bytes) -> CredencialNueva: ...

    @abstractmethod
    def opciones_de_entrada(self, *, permitir: list[Passkey], exigir_verificacion: bool) -> Reto:
        """`permitir` vacía: discoverable credentials (el autenticador ofrece las suyas para este sitio)."""

    @abstractmethod
    def credencial(self, respuesta: dict) -> tuple[bytes, bytes | None]:
        """(rawId, userHandle) de una respuesta, sin comprobar nada: para saber de qué passkey es."""

    @abstractmethod
    def comprobar_entrada(
        self, respuesta: dict, challenge: bytes, passkey: Passkey, *, exigir_verificacion: bool
    ) -> FirmaComprobada: ...
