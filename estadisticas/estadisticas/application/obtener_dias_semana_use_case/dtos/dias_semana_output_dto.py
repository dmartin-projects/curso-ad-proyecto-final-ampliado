# estadisticas/application/obtener_dias_semana_use_case/dtos/dias_semana_output_dto.py (módulo 89)
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from estadisticas.application.obtener_dias_semana_use_case.dtos.dia_semana_output_dto import DiaSemanaOutputDTO


class DiasSemanaOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    hogar_id: int
    ultimo_evento: datetime | None
    desde: date
    hasta: date  # el último día contado (el mes en curso, solo hasta hoy)
    dias: list[DiaSemanaOutputDTO]
