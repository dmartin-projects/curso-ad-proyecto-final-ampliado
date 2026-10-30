# asistente/application/compactar_conversacion_use_case/i_compactar_conversacion_use_case.py (módulo 99)
from abc import ABC, abstractmethod

from asistente.application.compactar_conversacion_use_case.dtos.compactar_conversacion_input_dto import (
    CompactarConversacionInputDTO,
)


class ICompactarConversacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CompactarConversacionInputDTO) -> bool:
        """Resume lo antiguo si la conversación ya no cabe holgada; devuelve si ha resumido."""
