# usuarios/application/solicitar_registro_use_case/dtos/solicitar_registro_input_dto.py (módulos 35 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class SolicitarRegistroInputDTO:
    email: str
    nombre: str = ""
    apellidos: str = ""
