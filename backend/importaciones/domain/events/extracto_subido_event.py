# importaciones/domain/events/extracto_subido_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractoSubidoEvent:
    importacion_id: int  # → analizarlo en segundo plano
