# usuarios/application/obtener_seguridad_use_case/dtos/obtener_seguridad_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerSeguridadInputDTO:
    usuario_id: int
