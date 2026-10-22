# oauth/application/retirar_acceso_use_case/dtos/retirar_acceso_input_dto.py (ejercicio 1 del módulo 90)
from dataclasses import dataclass


@dataclass(frozen=True)
class RetirarAccesoInputDTO:
    usuario_id: int
    client_id: str
