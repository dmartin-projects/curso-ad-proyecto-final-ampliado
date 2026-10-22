# estadisticas/infrastructure/api/v2/schemas/tendencia_con_tasa_schema.py (módulo 89, ejercicio 2)
from datetime import datetime

from pydantic import BaseModel

from estadisticas.infrastructure.api.v2.schemas.mes_con_tasa_schema import MesConTasa


class TendenciaConTasa(BaseModel):
    hogar_id: int
    ultimo_evento: datetime | None
    meses: list[MesConTasa]
