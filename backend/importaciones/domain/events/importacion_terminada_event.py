# importaciones/domain/events/importacion_terminada_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ImportacionTerminadaEvent:
    importacion_id: int
    formato: str
    completada: bool  # False: con error
    creados: int = 0  # → métricas (módulo 84) y notificación
