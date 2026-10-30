# asistente/application/crear_carpeta_use_case/dtos/crear_carpeta_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class CrearCarpetaInputDTO:
    hogar_id: int
    actor: Actor
    nombre: str
