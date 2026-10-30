# asistente/application/eliminar_conversacion_use_case/i_eliminar_conversacion_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.eliminar_conversacion_use_case.dtos.eliminar_conversacion_input_dto import (
    EliminarConversacionInputDTO,
)


class IEliminarConversacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarConversacionInputDTO) -> None:
        """Con todos sus mensajes y sus propuestas pendientes."""
