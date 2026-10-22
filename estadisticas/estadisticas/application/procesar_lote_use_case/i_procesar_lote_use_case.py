# estadisticas/application/procesar_lote_use_case/i_procesar_lote_use_case.py (módulo 89)
from abc import ABC, abstractmethod

from estadisticas.application.procesar_lote_use_case.dtos.procesar_lote_input_dto import ProcesarLoteInputDTO


class IProcesarLoteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ProcesarLoteInputDTO) -> int: ...
