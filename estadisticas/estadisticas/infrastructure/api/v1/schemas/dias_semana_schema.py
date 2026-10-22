# estadisticas/infrastructure/api/v1/schemas/dias_semana_schema.py (módulos 85 y 89)
from datetime import date, datetime

from pydantic import BaseModel

from estadisticas.infrastructure.api.v1.schemas.dia_semana_schema import DiaSemana


class DiasSemana(BaseModel):
    hogar_id: int
    ultimo_evento: datetime | None
    desde: date
    hasta: date  # el último día contado (el mes en curso, solo hasta hoy)
    dias: list[DiaSemana]
