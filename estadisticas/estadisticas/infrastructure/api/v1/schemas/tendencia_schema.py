# estadisticas/infrastructure/api/v1/schemas/tendencia_schema.py (módulos 85 y 89)
from datetime import datetime

from pydantic import BaseModel

from estadisticas.infrastructure.api.v1.schemas.mes_schema import Mes


class Tendencia(BaseModel):
    hogar_id: int
    # Cuándo se publicó el último cambio que ya está aplicado. El servicio va unos instantes por detrás de
    # Django (consistencia eventual): la interfaz puede decir "datos de hace X segundos"
    ultimo_evento: datetime | None
    meses: list[Mes]
