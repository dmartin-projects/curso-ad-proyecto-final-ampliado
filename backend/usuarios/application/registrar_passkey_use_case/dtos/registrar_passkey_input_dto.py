# usuarios/application/registrar_passkey_use_case/dtos/registrar_passkey_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistrarPasskeyInputDTO:
    usuario_id: int
    nombre: str
    respuesta: dict  # la de navigator.credentials.create(), en JSON (toJSON())
