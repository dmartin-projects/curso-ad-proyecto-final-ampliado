# usuarios/application/empezar_totp_use_case/dtos/empezar_totp_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class EmpezarTotpInputDTO:
    usuario_id: int
    cuenta: str  # el email: lo que enseña la app del móvil junto a «Gastos»
