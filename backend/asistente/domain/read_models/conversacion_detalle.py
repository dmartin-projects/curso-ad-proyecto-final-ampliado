# asistente/domain/read_models/conversacion_detalle.py — una conversación con sus mensajes visibles (módulo 97)
from dataclasses import dataclass

from asistente.domain.read_models.conversacion_listada import ConversacionListada
from asistente.domain.read_models.mensaje_visible import MensajeVisible


@dataclass(frozen=True, slots=True)
class ConversacionDetalle:
    conversacion: ConversacionListada
    mensajes: tuple[MensajeVisible, ...]
