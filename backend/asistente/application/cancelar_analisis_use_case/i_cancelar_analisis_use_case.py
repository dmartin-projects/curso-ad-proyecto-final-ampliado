# asistente/application/cancelar_analisis_use_case/i_cancelar_analisis_use_case.py (ejercicio 1 del 105)
from abc import ABC, abstractmethod

from asistente.application.cancelar_analisis_use_case.dtos.cancelar_analisis_input_dto import CancelarAnalisisInputDTO


class ICancelarAnalisisUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CancelarAnalisisInputDTO) -> None: ...
