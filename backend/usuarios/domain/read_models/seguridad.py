# usuarios/domain/read_models/seguridad.py — la verificación en dos pasos y las passkeys de una cuenta (módulo 92)
from dataclasses import dataclass

from usuarios.domain.read_models.passkey_registrada import PasskeyRegistrada


@dataclass(frozen=True, slots=True)
class Seguridad:
    mfa: bool  # la verificación en dos pasos (TOTP) está activa
    codigos_restantes: int
    passkeys: tuple[PasskeyRegistrada, ...] = ()
