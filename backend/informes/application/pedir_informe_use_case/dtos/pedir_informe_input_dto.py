# informes/application/pedir_informe_use_case/dtos/pedir_informe_input_dto.py (módulos 78 y 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class PedirInformeInputDTO:
    hogar_id: int
    actor: Actor
    mes: Mes
    enviar: bool = False
