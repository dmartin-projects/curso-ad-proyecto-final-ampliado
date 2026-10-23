# usuarios/infrastructure/mfa/codigo_qr_segno.py — ICodigoQr con segno: el QR del alta del TOTP, en SVG (módulo 92)
import segno

from usuarios.application.ports.i_codigo_qr import ICodigoQr


class CodigoQrSegno(ICodigoQr):
    def svg(self, texto: str) -> str:
        """El QR del otpauth://, como data URI de un SVG: la SPA lo pinta en un <img> (la CSP admite img-src data:).
        Se genera en el servidor: el secreto ya ha llegado a la SPA para escribirlo a mano, y así no hace falta otra
        librería en Angular."""
        return segno.make(texto, error="m").svg_data_uri(scale=5, border=2)
