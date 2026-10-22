# informes/application/listar_informes_use_case/dtos/listar_informes_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarInformesInputDTO:
    hogar_id: int
    actor: Actor
