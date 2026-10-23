# usuarios/application/ports/i_totp.py (módulo 92)
from abc import ABC, abstractmethod
from datetime import datetime


class ITotp(ABC):
    """RFC 6238: códigos de 6 cifras cada 30 s a partir de un secreto compartido."""

    @abstractmethod
    def nuevo_secreto(self) -> str: ...

    @abstractmethod
    def paso(self, secreto: str, codigo: str, ahora: datetime) -> int | None:
        """El paso (ahora ±1, por los relojes que no van a la par) cuyo código es `codigo`; None si ninguno."""

    @abstractmethod
    def uri(self, secreto: str, cuenta: str) -> str:
        """otpauth://totp/Gastos:ana@…?secret=…&issuer=Gastos: lo que lleva el QR."""
        ...
