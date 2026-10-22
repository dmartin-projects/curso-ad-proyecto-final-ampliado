# eventos/domain/bo/evento_pendiente.py — lo que el relay tiene que publicar (módulos 85 y 88)
from dataclasses import dataclass
from datetime import datetime

from eventos.domain.vo.mensaje import Mensaje


@dataclass(frozen=True)
class EventoPendiente:
    """Un mensaje del outbox que aún no ha salido. El id es su versión: crece con cada cambio."""

    id: int
    mensaje: Mensaje
    traceparent: str  # la traza de quien hizo el cambio (módulo 84)
    creado: datetime
