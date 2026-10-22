# informes/application/generar_informe_use_case/i_generar_informe_use_case.py (módulos 78 y 88)
from abc import ABC, abstractmethod

from informes.application.generar_informe_use_case.dtos.generar_informe_input_dto import GenerarInformeInputDTO
from informes.application.shared.dtos.informe_output_dto import InformeOutputDTO


class IGenerarInformeUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: GenerarInformeInputDTO) -> InformeOutputDTO: ...
