# asistente/domain/repositories/i_grafico_fijado_query_service.py — los gráficos fijados de un hogar (módulo 97)
from abc import ABC, abstractmethod

from asistente.domain.read_models.grafico_fijado_listado import GraficoFijadoListado


class IGraficoFijadoQueryService(ABC):
    @abstractmethod
    def listar(self, hogar_id: int) -> tuple[GraficoFijadoListado, ...]:
        """En el orden en que se fijaron."""
