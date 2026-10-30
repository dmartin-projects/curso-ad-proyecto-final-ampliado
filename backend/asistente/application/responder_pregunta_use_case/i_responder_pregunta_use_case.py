# asistente/application/responder_pregunta_use_case/i_responder_pregunta_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.responder_pregunta_use_case.dtos.responder_pregunta_input_dto import (
    ResponderPreguntaInputDTO,
)


class IResponderPreguntaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ResponderPreguntaInputDTO) -> int | None:
        """Pregunta y respuesta guardadas en la conversación, con cada paso emitido por el emisor. Devuelve el id del
        mensaje de la respuesta, o None si la pregunta se canceló o el modelo no estaba disponible."""
