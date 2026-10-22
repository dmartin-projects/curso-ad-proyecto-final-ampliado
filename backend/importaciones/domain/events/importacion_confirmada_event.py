# importaciones/domain/events/importacion_confirmada_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ImportacionConfirmadaEvent:
    importacion_id: int
    filas: tuple[int, ...]  # → importarlas por lotes, en paralelo (un chord de Celery, módulo 26)
