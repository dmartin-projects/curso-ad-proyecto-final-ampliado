# informes/application/listar_hogares_sin_informe_use_case/dtos/listar_hogares_sin_informe_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class ListarHogaresSinInformeInputDTO:
    mes: Mes
