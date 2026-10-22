# informes/application/obtener_informe_use_case/i_obtener_informe_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from informes.application.obtener_informe_use_case.dtos.obtener_informe_input_dto import ObtenerInformeInputDTO
from informes.application.shared.dtos.informe_listado_output_dto import InformeListadoOutputDTO


class IObtenerInformeUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerInformeInputDTO) -> InformeListadoOutputDTO | None: ...
