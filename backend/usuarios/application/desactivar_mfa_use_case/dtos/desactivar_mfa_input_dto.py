# usuarios/application/desactivar_mfa_use_case/dtos/desactivar_mfa_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class DesactivarMfaInputDTO:
    usuario_id: int
