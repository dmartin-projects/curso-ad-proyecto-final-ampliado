# estadisticas/infrastructure/api/v1/parametros.py — query params comunes de la v1 (módulos 85 y 89)
from typing import Annotated

from fastapi import Query

Meses = Annotated[int, Query(ge=1, le=36)]
