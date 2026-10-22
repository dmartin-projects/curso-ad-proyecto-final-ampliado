# importaciones/application/confirmar_importacion_use_case/dtos/confirmar_importacion_input_dto.py (módulos 75 y 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ConfirmarImportacionInputDTO:
    hogar_id: int
    actor: Actor
    importacion_id: int
    separar: tuple[int, ...] = ()  # filas a conciliar que la persona quiere importar como movimientos nuevos
