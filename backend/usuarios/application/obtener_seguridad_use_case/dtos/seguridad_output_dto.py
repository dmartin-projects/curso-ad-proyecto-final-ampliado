# usuarios/application/obtener_seguridad_use_case/dtos/seguridad_output_dto.py (módulo 92)
from dataclasses import dataclass

from usuarios.application.obtener_seguridad_use_case.dtos.passkey_registrada_output_dto import (
    PasskeyRegistradaOutputDTO,
)
from usuarios.domain.read_models.seguridad import Seguridad


@dataclass(frozen=True, slots=True)
class SeguridadOutputDTO:
    mfa: bool  # la verificación en dos pasos (TOTP) está activa
    codigos_restantes: int
    passkeys: tuple[PasskeyRegistradaOutputDTO, ...]

    @classmethod
    def desde_read_model(cls, rm: Seguridad) -> "SeguridadOutputDTO":
        return cls(
            rm.mfa, rm.codigos_restantes, tuple(PasskeyRegistradaOutputDTO.desde_read_model(p) for p in rm.passkeys)
        )
