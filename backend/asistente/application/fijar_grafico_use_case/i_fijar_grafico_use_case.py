# asistente/application/fijar_grafico_use_case/i_fijar_grafico_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.fijar_grafico_use_case.dtos.fijar_grafico_input_dto import FijarGraficoInputDTO
from asistente.application.shared.dtos.grafico_fijado_output_dto import GraficoFijadoOutputDTO


class IFijarGraficoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: FijarGraficoInputDTO) -> GraficoFijadoOutputDTO:
        """Fija un gráfico (su especificación) en el dashboard del hogar, si se puede calcular."""
