# usuarios/application/ports/i_codigo_qr.py — el QR del alta del TOTP (módulo 92)
from abc import ABC, abstractmethod


class ICodigoQr(ABC):
    @abstractmethod
    def svg(self, texto: str) -> str:
        """El QR de `texto` (el otpauth://), como data URI de un SVG: la SPA lo pinta en un <img>."""
