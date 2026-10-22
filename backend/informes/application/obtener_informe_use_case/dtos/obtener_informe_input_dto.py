# informes/application/obtener_informe_use_case/dtos/obtener_informe_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class ObtenerInformeInputDTO:
    hogar_id: int
    actor: Actor
    mes: Mes
