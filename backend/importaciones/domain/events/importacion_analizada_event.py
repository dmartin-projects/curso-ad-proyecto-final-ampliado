# importaciones/domain/events/importacion_analizada_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ImportacionAnalizadaEvent:
    importacion_id: int  # → la vista previa está lista (notificación)
