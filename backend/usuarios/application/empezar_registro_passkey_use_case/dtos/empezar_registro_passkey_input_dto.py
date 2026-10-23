# usuarios/application/empezar_registro_passkey_use_case/dtos/empezar_registro_passkey_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class EmpezarRegistroPasskeyInputDTO:
    usuario_id: int
    cuenta: str
    nombre: str
