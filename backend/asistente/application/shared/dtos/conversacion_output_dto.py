# asistente/application/shared/dtos/conversacion_output_dto.py (módulo 97)
from dataclasses import dataclass
from datetime import datetime

from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.read_models.conversacion_listada import ConversacionListada


@dataclass(frozen=True, slots=True)
class ConversacionOutputDTO:
    id: int
    titulo: str
    carpeta_id: int | None
    actualizada: datetime | None = None  # solo al leer (el BO no la tiene: la pone el repositorio)

    @classmethod
    def desde_bo(cls, c: Conversacion) -> "ConversacionOutputDTO":
        return cls(c.id, c.titulo, c.carpeta_id)

    @classmethod
    def desde_read_model(cls, c: ConversacionListada) -> "ConversacionOutputDTO":
        return cls(c.id, c.titulo, c.carpeta_id, c.actualizada)
