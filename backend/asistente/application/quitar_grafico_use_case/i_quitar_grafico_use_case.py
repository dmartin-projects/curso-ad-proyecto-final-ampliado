# asistente/application/quitar_grafico_use_case/i_quitar_grafico_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.quitar_grafico_use_case.dtos.quitar_grafico_input_dto import QuitarGraficoInputDTO


class IQuitarGraficoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: QuitarGraficoInputDTO) -> None:
        """Lo quita del dashboard del hogar."""
