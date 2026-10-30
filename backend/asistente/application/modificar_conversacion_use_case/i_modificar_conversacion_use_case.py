# asistente/application/modificar_conversacion_use_case/i_modificar_conversacion_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.modificar_conversacion_use_case.dtos.modificar_conversacion_input_dto import (
    ModificarConversacionInputDTO,
)
from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO


class IModificarConversacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ModificarConversacionInputDTO) -> ConversacionOutputDTO:
        """Cambiar el título (desde entonces lo elige la persona) o la carpeta (None: fuera de todas)."""
