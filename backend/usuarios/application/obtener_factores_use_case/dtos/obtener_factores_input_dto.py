# usuarios/application/obtener_factores_use_case/dtos/obtener_factores_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerFactoresInputDTO:
    usuario_id: int
