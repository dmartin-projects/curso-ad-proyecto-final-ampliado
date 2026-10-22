# estadisticas/infrastructure/api/v2/schemas/mes_con_tasa_schema.py (módulo 89, ejercicio 2)
#
# Los schemas de la v2 son suyos: la v1 sigue con los de api/v1/schemas sin enterarse. Nombres distintos de los de la
# v1, porque OpenAPI tiene un solo espacio de nombres para los esquemas.
from decimal import Decimal

from pydantic import BaseModel


class MesConTasa(BaseModel):
    mes: str
    gastos: Decimal
    ingresos: Decimal
    ahorro: Decimal
    tasa_ahorro: Decimal | None  # % de los ingresos; null si no hubo ingresos
