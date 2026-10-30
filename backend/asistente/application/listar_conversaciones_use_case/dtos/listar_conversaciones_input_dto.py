# asistente/application/listar_conversaciones_use_case/dtos/listar_conversaciones_input_dto.py (módulo 97)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarConversacionesInputDTO:
    hogar_id: int
    actor: Actor
    carpeta_id: int | None = None
    busqueda: str | None = None  # ejercicio 2
