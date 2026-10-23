# usuarios/application/regenerar_codigos_use_case/dtos/regenerar_codigos_input_dto.py (módulo 92, ejercicio 2)
from dataclasses import dataclass


@dataclass(frozen=True)
class RegenerarCodigosInputDTO:
    usuario_id: int
