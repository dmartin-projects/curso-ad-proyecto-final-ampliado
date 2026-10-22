# estadisticas/infrastructure/api/v1/schemas/mes_sin_revisar_schema.py (módulos 85 y 89)
from decimal import Decimal

from pydantic import BaseModel


class MesSinRevisar(BaseModel):
    mes: str
    movimientos: int
    gastos: Decimal
