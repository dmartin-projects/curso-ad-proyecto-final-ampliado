# estadisticas/application/obtener_sin_revisar_use_case/dtos/sin_revisar_output_dto.py (módulo 89)
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from estadisticas.application.obtener_sin_revisar_use_case.dtos.mes_sin_revisar_output_dto import (
    MesSinRevisarOutputDTO,
)


class SinRevisarOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    hogar_id: int
    ultimo_evento: datetime | None
    meses: list[MesSinRevisarOutputDTO]
