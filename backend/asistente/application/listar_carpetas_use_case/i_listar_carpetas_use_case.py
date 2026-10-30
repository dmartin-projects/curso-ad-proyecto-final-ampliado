# asistente/application/listar_carpetas_use_case/i_listar_carpetas_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.listar_carpetas_use_case.dtos.listar_carpetas_input_dto import ListarCarpetasInputDTO
from asistente.application.shared.dtos.carpeta_output_dto import CarpetaOutputDTO


class IListarCarpetasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarCarpetasInputDTO) -> list[CarpetaOutputDTO]:
        """Las de quien pide en ese hogar, por nombre, con cuántas conversaciones tiene cada una."""
