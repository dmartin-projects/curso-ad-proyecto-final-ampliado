# usuarios/application/establecer_contrasena_use_case/dtos/establecer_contrasena_input_dto.py (módulo 91)
from dataclasses import dataclass


@dataclass(frozen=True)
class EstablecerContrasenaInputDTO:
    usuario_id: int
    nueva: str
