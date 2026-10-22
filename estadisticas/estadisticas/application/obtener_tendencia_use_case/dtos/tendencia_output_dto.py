# estadisticas/application/obtener_tendencia_use_case/dtos/tendencia_output_dto.py (módulo 89)
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from estadisticas.application.obtener_tendencia_use_case.dtos.mes_de_tendencia_output_dto import (
    MesDeTendenciaOutputDTO,
)


class TendenciaOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    hogar_id: int
    # Cuándo se publicó el último cambio que ya está aplicado. El servicio va unos instantes por detrás de
    # Django (consistencia eventual): la interfaz puede decir "datos de hace X segundos"
    ultimo_evento: datetime | None
    meses: list[MesDeTendenciaOutputDTO]
