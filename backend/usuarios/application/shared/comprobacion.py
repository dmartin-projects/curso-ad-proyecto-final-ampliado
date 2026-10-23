# usuarios/application/shared/comprobacion.py — el resultado de comprobar un factor (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class Comprobacion:
    error: Exception | None = None  # CodigoNoValidoException, PasskeyNoValidaException o ContrasenaIncorrectaException
    sincronizada: bool = False  # la passkey (para el amr)
