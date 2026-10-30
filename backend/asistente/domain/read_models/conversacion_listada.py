# asistente/domain/read_models/conversacion_listada.py — una conversación en la lista del chat (módulo 97)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ConversacionListada:
    id: int
    titulo: str
    carpeta_id: int | None
    actualizada: datetime
