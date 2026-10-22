# estadisticas/application/obtener_tendencia_use_case/dtos/obtener_tendencia_input_dto.py (módulo 89)
from pydantic import BaseModel, ConfigDict


class ObtenerTendenciaInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    hogar_id: int
    meses: int
    hasta: str | None = None  # "2026-10"; sin él, el mes de hoy
