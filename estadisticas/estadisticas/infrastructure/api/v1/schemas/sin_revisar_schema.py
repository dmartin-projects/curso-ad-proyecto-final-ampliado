# estadisticas/infrastructure/api/v1/schemas/sin_revisar_schema.py (módulos 85 y 89)
from datetime import datetime

from pydantic import BaseModel

from estadisticas.infrastructure.api.v1.schemas.mes_sin_revisar_schema import MesSinRevisar


class SinRevisar(BaseModel):
    hogar_id: int
    ultimo_evento: datetime | None
    meses: list[MesSinRevisar]
