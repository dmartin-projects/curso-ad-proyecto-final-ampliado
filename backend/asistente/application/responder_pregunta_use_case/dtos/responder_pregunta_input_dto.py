# asistente/application/responder_pregunta_use_case/dtos/responder_pregunta_input_dto.py (módulo 97)
from dataclasses import dataclass

from asistente.application.chat.adjunto import Adjunto
from asistente.application.ports.i_emisor_de_eventos import IEmisorDeEventos
from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ResponderPreguntaInputDTO:
    hogar_id: int
    actor: Actor
    conversacion_id: int
    texto: str
    emisor: IEmisorDeEventos  # por dónde salen los pasos: lo pone el adapter de entrada (la vista SSE, un test)
    adjunto: Adjunto | None = None
