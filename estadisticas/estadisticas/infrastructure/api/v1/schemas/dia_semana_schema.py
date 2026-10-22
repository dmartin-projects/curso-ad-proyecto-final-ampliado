# estadisticas/infrastructure/api/v1/schemas/dia_semana_schema.py (módulos 85 y 89)
from decimal import Decimal

from pydantic import BaseModel


class DiaSemana(BaseModel):
    dia: int  # 1 = lunes … 7 = domingo (ISO)
    nombre: str
    gasto_medio: Decimal
