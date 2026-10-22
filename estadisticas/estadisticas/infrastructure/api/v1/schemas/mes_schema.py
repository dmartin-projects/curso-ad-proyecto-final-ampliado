# estadisticas/infrastructure/api/v1/schemas/mes_schema.py (módulos 85 y 89)
#
# Un schema de la API: el equivalente FastAPI de un serializer de DRF. El nombre de la clase es el del esquema en
# OpenAPI (components/schemas/Mes): por eso no lleva sufijo, como el modelo de Django. Sin docstring: iría al
# esquema como "description".
from decimal import Decimal

from pydantic import BaseModel


class Mes(BaseModel):
    mes: str  # "2026-10"
    gastos: Decimal
    ingresos: Decimal
    ahorro: Decimal
