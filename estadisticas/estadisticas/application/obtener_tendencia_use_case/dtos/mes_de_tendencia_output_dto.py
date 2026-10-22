# estadisticas/application/obtener_tendencia_use_case/dtos/mes_de_tendencia_output_dto.py (módulo 89)
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MesDeTendenciaOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    mes: str  # "2026-10"
    gastos: Decimal
    ingresos: Decimal
    ahorro: Decimal
