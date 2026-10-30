# asistente/application/listar_graficos_fijados_use_case/i_listar_graficos_fijados_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.listar_graficos_fijados_use_case.dtos.listar_graficos_fijados_input_dto import (
    ListarGraficosFijadosInputDTO,
)
from asistente.application.shared.dtos.grafico_fijado_output_dto import GraficoFijadoOutputDTO


class IListarGraficosFijadosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarGraficosFijadosInputDTO) -> list[GraficoFijadoOutputDTO]:
        """Los del hogar, recalculados con el Actor de quien mira."""
