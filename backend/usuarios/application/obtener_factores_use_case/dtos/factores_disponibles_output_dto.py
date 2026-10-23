# usuarios/application/obtener_factores_use_case/dtos/factores_disponibles_output_dto.py (módulo 92)
from dataclasses import dataclass

from usuarios.domain.vo.factores_disponibles import FactoresDisponibles


@dataclass(frozen=True)
class FactoresDisponiblesOutputDTO:
    totp: bool
    passkeys: bool
    recuperacion: bool
    contrasena: bool  # solo para el step-up de una cuenta sin MFA
    lista: list[str]  # "totp", "passkey", "recuperacion", "contrasena": los que tiene
    segundos: list[str]  # los que completan el segundo paso del login

    @classmethod
    def desde_vo(cls, factores: FactoresDisponibles) -> "FactoresDisponiblesOutputDTO":
        return cls(
            factores.totp, factores.passkeys, factores.recuperacion, factores.contrasena, factores.lista(),
            factores.segundos(),
        )  # fmt: skip
