# importaciones/application/analizar_extracto_use_case/dtos/analizar_extracto_input_dto.py (módulos 75 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class AnalizarExtractoInputDTO:
    importacion_id: int
