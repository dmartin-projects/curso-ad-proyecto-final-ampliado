# estadisticas/application/obtener_sin_revisar_use_case/dtos/obtener_sin_revisar_input_dto.py (módulo 89)
from pydantic import BaseModel, ConfigDict


class ObtenerSinRevisarInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    hogar_id: int
    meses: int
    hasta: str | None = None  # "2026-10"; sin él, el mes de hoy
