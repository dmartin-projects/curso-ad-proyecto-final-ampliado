# usuarios/application/cambiar_contrasena_use_case/dtos/cambiar_contrasena_input_dto.py (módulos 35 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class CambiarContrasenaInputDTO:
    usuario_id: int
    actual: str
    nueva: str
