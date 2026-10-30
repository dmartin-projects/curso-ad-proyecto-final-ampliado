# asistente/application/compactar_conversacion_use_case/dtos/compactar_conversacion_input_dto.py (módulo 99)
from dataclasses import dataclass


@dataclass(frozen=True)
class CompactarConversacionInputDTO:
    usuario_id: int
    hogar_id: int
    conversacion_id: int
