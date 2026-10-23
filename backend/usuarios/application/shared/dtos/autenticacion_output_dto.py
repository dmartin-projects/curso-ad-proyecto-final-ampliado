# usuarios/application/shared/dtos/autenticacion_output_dto.py — cómo y cuándo se autenticó una sesión (módulo 92)
from dataclasses import dataclass
from datetime import datetime

from usuarios.domain.enums.factor import Factor
from usuarios.domain.vo.autenticacion import Autenticacion


@dataclass(frozen=True)
class AutenticacionOutputDTO:
    factores: frozenset[Factor]
    momento: datetime  # el `auth_time` de OIDC
    passkey_sincronizada: bool
    multifactor: bool
    amr: list[str]  # RFC 8176: "pwd", "otp", "fed", "hwk"/"swk", "user", "mfa"
    acr: str  # urn:gastos:acr:1fa o urn:gastos:acr:mfa

    @classmethod
    def desde_vo(cls, autenticacion: Autenticacion) -> "AutenticacionOutputDTO":
        return cls(
            factores=autenticacion.factores,
            momento=autenticacion.momento,
            passkey_sincronizada=autenticacion.passkey_sincronizada,
            multifactor=autenticacion.multifactor,
            amr=autenticacion.amr(),
            acr=autenticacion.acr(),
        )
