# asistente/application/ver_contexto_use_case/dtos/parte_del_contexto_output_dto.py (módulo 99, ejercicio 2)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParteDelContextoOutputDTO:
    rol: str  # memoria, usuario, modelo
    texto: str
    tokens: int  # estimados
