# backoffice/application/obtener_tarea_programada_use_case/dtos/obtener_tarea_programada_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerTareaProgramadaInputDTO:
    tarea_id: int
