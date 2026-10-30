# asistente/application/shared/dtos/conversacion_detalle_output_dto.py (módulo 97)
from dataclasses import dataclass

from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO
from asistente.application.shared.dtos.mensaje_output_dto import MensajeOutputDTO


@dataclass(frozen=True, slots=True)
class ConversacionDetalleOutputDTO:
    conversacion: ConversacionOutputDTO
    mensajes: list[MensajeOutputDTO]
