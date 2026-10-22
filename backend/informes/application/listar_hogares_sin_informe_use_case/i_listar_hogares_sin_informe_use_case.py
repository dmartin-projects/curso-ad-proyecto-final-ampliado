# informes/application/listar_hogares_sin_informe_use_case/i_listar_hogares_sin_informe_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from informes.application.listar_hogares_sin_informe_use_case.dtos.listar_hogares_sin_informe_input_dto import (
    ListarHogaresSinInformeInputDTO,
)


class IListarHogaresSinInformeUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarHogaresSinInformeInputDTO) -> list[int]: ...
