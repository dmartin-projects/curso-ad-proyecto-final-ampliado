# asistente/application/analizar_mes_use_case/i_analizar_mes_use_case.py (módulo 105)
from abc import ABC, abstractmethod

from asistente.application.analizar_mes_use_case.dtos.analizar_mes_input_dto import AnalizarMesInputDTO


class IAnalizarMesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: AnalizarMesInputDTO) -> int | None:
        """El id de la conversación con el análisis; None si el modelo no está disponible."""
