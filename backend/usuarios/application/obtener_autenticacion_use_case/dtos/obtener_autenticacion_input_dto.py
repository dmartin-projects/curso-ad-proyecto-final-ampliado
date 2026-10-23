# usuarios/application/obtener_autenticacion_use_case/dtos/obtener_autenticacion_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerAutenticacionInputDTO:
    sid: str
