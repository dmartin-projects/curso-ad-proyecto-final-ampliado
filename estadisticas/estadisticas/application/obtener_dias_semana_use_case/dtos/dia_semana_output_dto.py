# estadisticas/application/obtener_dias_semana_use_case/dtos/dia_semana_output_dto.py (módulo 89)
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DiaSemanaOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    dia: int  # 1 = lunes … 7 = domingo (ISO)
    nombre: str
    gasto_medio: Decimal
