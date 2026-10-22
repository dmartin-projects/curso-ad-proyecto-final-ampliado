# informes/application/pedir_informe_use_case/i_pedir_informe_use_case.py (módulos 78 y 88)
from abc import ABC, abstractmethod

from core.domain.vo.mes import Mes
from informes.application.pedir_informe_use_case.dtos.pedir_informe_input_dto import PedirInformeInputDTO


class IPedirInformeUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: PedirInformeInputDTO) -> Mes: ...
