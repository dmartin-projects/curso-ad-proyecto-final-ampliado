# usuarios/domain/enums/factor.py — con qué ha demostrado alguien quién es (módulo 92)
from enum import StrEnum


class Factor(StrEnum):
    """Con qué ha demostrado alguien quién es. Primeros factores: contraseña, proveedor y passkey (que, con
    verificación del usuario, ya es multifactor). Segundos: TOTP, passkey y código de recuperación."""

    CONTRASENA = "contrasena"
    PROVEEDOR = "proveedor"  # Google, GitHub, Apple… (módulo 91)
    TOTP = "totp"
    RECUPERACION = "recuperacion"
    PASSKEY = "passkey"
