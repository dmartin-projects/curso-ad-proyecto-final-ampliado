# importaciones/application/analizar_extracto_use_case/i_analizar_extracto_use_case.py (módulos 75 y 88)
from abc import ABC, abstractmethod

from importaciones.application.analizar_extracto_use_case.dtos.analizar_extracto_input_dto import (
    AnalizarExtractoInputDTO,
)
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO


class IAnalizarExtractoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: AnalizarExtractoInputDTO) -> ImportacionOutputDTO | None: ...
