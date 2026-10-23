# usuarios/application/empezar_totp_use_case/dtos/alta_totp_output_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AltaTotpOutputDTO:
    secreto: str  # para escribirlo a mano si no se puede leer el QR
    uri: str  # otpauth://…: lo que lleva el QR
    qr: str  # el QR, como data URI de un SVG
