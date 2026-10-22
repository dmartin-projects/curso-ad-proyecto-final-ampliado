# estadisticas/application/obtener_sin_revisar_use_case/dtos/mes_sin_revisar_output_dto.py (módulo 89)
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MesSinRevisarOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    mes: str
    movimientos: int
    gastos: Decimal
