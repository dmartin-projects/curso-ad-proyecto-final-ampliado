# backoffice/application/shared/dtos/tarea_programada_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from backoffice.domain.read_models.tarea_programada_soporte import TareaProgramadaSoporte


@dataclass(frozen=True, slots=True)
class TareaProgramadaSoporteOutputDTO:
    id: int
    name: str
    task: str
    horario: str | None
    enabled: bool
    last_run_at: datetime | None
    total_run_count: int

    @classmethod
    def desde_read_model(cls, rm: TareaProgramadaSoporte) -> "TareaProgramadaSoporteOutputDTO":
        return cls(
            id=rm.id,
            name=rm.name,
            task=rm.task,
            horario=rm.horario,
            enabled=rm.enabled,
            last_run_at=rm.last_run_at,
            total_run_count=rm.total_run_count,
        )
