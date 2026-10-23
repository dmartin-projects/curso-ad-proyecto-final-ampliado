# usuarios/application/iniciar_sesion_use_case/dtos/iniciar_sesion_input_dto.py (módulo 91)
from dataclasses import dataclass


@dataclass(frozen=True)
class IniciarSesionInputDTO:
    usuario_id: int
