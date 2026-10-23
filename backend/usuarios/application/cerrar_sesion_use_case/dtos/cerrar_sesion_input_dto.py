# usuarios/application/cerrar_sesion_use_case/dtos/cerrar_sesion_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class CerrarSesionInputDTO:
    usuario_id: int
    sid: str
