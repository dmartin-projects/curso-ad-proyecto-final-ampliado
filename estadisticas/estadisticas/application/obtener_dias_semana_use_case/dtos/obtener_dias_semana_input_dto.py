# estadisticas/application/obtener_dias_semana_use_case/dtos/obtener_dias_semana_input_dto.py (módulo 89)
from pydantic import BaseModel, ConfigDict


class ObtenerDiasSemanaInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    hogar_id: int
    meses: int
    hasta: str | None = None  # "2026-10"; sin él, el mes de hoy
