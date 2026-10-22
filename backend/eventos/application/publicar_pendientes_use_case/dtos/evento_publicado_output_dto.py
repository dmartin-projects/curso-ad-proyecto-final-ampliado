# eventos/application/publicar_pendientes_use_case/dtos/evento_publicado_output_dto.py (módulos 85 y 88)
from dataclasses import dataclass
from datetime import datetime

from eventos.domain.bo.evento_pendiente import EventoPendiente


@dataclass(frozen=True, slots=True)
class EventoPublicadoOutputDTO:
    """Lo que necesita quien publica para sus métricas: qué, a qué topic y desde cuándo esperaba."""

    id: int
    topic: str
    creado: datetime

    @classmethod
    def desde_bo(cls, p: EventoPendiente) -> "EventoPublicadoOutputDTO":
        return cls(id=p.id, topic=p.mensaje.topic, creado=p.creado)
