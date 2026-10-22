# importaciones/application/importar_lote_use_case/i_importar_lote_use_case.py (módulos 75 y 88)
from abc import ABC, abstractmethod

from importaciones.application.importar_lote_use_case.dtos.importar_lote_input_dto import ImportarLoteInputDTO


class IImportarLoteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ImportarLoteInputDTO) -> dict: ...
