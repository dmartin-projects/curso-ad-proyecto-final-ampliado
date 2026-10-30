# asistente/domain/repositories/i_grafico_fijado_command_repository.py — fijar y quitar gráficos (módulo 97)
from abc import ABC, abstractmethod

from asistente.domain.bo.grafico_fijado import GraficoFijado


class IGraficoFijadoCommandRepository(ABC):
    @abstractmethod
    def obtener(self, hogar_id: int, grafico_id: int) -> GraficoFijado:
        """El de ese hogar, o GraficoNoEncontradoException."""

    @abstractmethod
    def guardar(self, grafico: GraficoFijado) -> None: ...

    @abstractmethod
    def eliminar(self, grafico: GraficoFijado) -> None: ...
