# asistente/application/listar_conversaciones_use_case/i_listar_conversaciones_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.listar_conversaciones_use_case.dtos.listar_conversaciones_input_dto import (
    ListarConversacionesInputDTO,
)
from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO


class IListarConversacionesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarConversacionesInputDTO) -> list[ConversacionOutputDTO]:
        """Las de quien pide en ese hogar, las más recientes primero."""
