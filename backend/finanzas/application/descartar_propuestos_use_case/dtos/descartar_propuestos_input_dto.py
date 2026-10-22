# finanzas/application/descartar_propuestos_use_case/dtos/descartar_propuestos_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class DescartarPropuestosInputDTO:
    hogar_id: int
    actor: Actor
    ids: tuple[int, ...]
