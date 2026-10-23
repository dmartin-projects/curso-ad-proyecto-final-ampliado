# usuarios/application/borrar_passkey_use_case/dtos/borrar_passkey_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class BorrarPasskeyInputDTO:
    usuario_id: int
    passkey_id: int
