# asistente/application/modificar_carpeta_use_case/dtos/modificar_carpeta_input_dto.py (módulo 97, ejercicio 1)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ModificarCarpetaInputDTO:
    hogar_id: int
    actor: Actor
    carpeta_id: int
    nombre: str
