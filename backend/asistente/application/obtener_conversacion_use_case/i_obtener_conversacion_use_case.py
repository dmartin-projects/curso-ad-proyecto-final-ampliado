# asistente/application/obtener_conversacion_use_case/i_obtener_conversacion_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.obtener_conversacion_use_case.dtos.obtener_conversacion_input_dto import (
    ObtenerConversacionInputDTO,
)
from asistente.application.shared.dtos.conversacion_detalle_output_dto import ConversacionDetalleOutputDTO


class IObtenerConversacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerConversacionInputDTO) -> ConversacionDetalleOutputDTO | None:
        """La conversación con sus mensajes visibles, o None si no es de quien pide."""
