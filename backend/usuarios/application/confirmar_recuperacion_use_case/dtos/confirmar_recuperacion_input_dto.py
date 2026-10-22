# usuarios/application/confirmar_recuperacion_use_case/dtos/confirmar_recuperacion_input_dto.py (módulos 35 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ConfirmarRecuperacionInputDTO:
    uid: str
    token: str
    password: str
