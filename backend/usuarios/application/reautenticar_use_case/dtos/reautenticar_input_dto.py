# usuarios/application/reautenticar_use_case/dtos/reautenticar_input_dto.py (módulo 92)
from dataclasses import dataclass

from usuarios.domain.enums.factor import Factor


@dataclass(frozen=True)
class ReautenticarInputDTO:
    usuario_id: int
    sid: str
    factor: Factor
    codigo: str = ""  # el TOTP o la contraseña
    respuesta: dict | None = None
