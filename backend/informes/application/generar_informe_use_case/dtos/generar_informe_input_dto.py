# informes/application/generar_informe_use_case/dtos/generar_informe_input_dto.py (módulos 78 y 88)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class GenerarInformeInputDTO:
    hogar_id: int
    mes: Mes
    usuario_id: int | None = None  # None: lo genera Celery Beat, el día 1
    enviar: bool = True
