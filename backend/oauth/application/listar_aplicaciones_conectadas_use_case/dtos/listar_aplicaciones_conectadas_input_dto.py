# oauth/application/listar_aplicaciones_conectadas_use_case/dtos/listar_aplicaciones_conectadas_input_dto.py (ejercicio 1 del módulo 90)
from dataclasses import dataclass


@dataclass(frozen=True)
class ListarAplicacionesConectadasInputDTO:
    usuario_id: int
