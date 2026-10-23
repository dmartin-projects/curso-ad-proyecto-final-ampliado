# usuarios/application/confirmar_totp_use_case/dtos/confirmar_totp_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class ConfirmarTotpInputDTO:
    usuario_id: int
    codigo: str
