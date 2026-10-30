# asistente/application/crear_conversacion_use_case/i_crear_conversacion_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.crear_conversacion_use_case.dtos.crear_conversacion_input_dto import (
    CrearConversacionInputDTO,
)
from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO


class ICrearConversacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CrearConversacionInputDTO) -> ConversacionOutputDTO:
        """Una conversación vacía de quien pide, en su hogar (y, si se dice, en una de sus carpetas)."""
