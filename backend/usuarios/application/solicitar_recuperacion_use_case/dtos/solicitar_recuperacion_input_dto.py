# usuarios/application/solicitar_recuperacion_use_case/dtos/solicitar_recuperacion_input_dto.py (módulos 35 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class SolicitarRecuperacionInputDTO:
    email: str
