# usuarios/application/obtener_acceso_use_case/dtos/obtener_acceso_input_dto.py (módulo 91)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerAccesoInputDTO:
    usuario_id: int
