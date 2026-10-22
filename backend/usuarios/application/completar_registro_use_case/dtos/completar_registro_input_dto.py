# usuarios/application/completar_registro_use_case/dtos/completar_registro_input_dto.py (módulos 35 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class CompletarRegistroInputDTO:
    uid: str
    token: str
    password: str
