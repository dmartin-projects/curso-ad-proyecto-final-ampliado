# backoffice/domain/read_models/tarea_programada_soporte.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TareaProgramadaSoporte:
    id: int
    name: str
    task: str
    horario: str | None
    enabled: bool
    last_run_at: datetime | None
    total_run_count: int
