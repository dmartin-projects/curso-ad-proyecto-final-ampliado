# estadisticas/infrastructure/api/v1/routers/tendencia_router.py — GET /hogares/{hogar_id}/tendencia (módulos 85
# y 89)
#
# Solo traduce: parámetros → InputDTO → use case (del container, con Depends) → schema. Nada de SQL ni de fechas.
# OJO: el nombre de la función y su docstring son el operationId, el summary y la descripción del esquema OpenAPI
# (un cambio aquí cambia el contrato).
from typing import Annotated

from fastapi import APIRouter, Depends

from estadisticas.application.obtener_tendencia_use_case.dtos.obtener_tendencia_input_dto import (
    ObtenerTendenciaInputDTO,
)
from estadisticas.application.obtener_tendencia_use_case.i_obtener_tendencia_use_case import IObtenerTendenciaUseCase
from estadisticas.infrastructure import container
from estadisticas.infrastructure.api.dependencies.hogar_permitido import Hogar
from estadisticas.infrastructure.api.v1.parametros import Meses
from estadisticas.infrastructure.api.v1.schemas.tendencia_schema import Tendencia

router = APIRouter()


@router.get("/hogares/{hogar_id}/tendencia", response_model=Tendencia)
def tendencia(
    hogar_id: Hogar,
    caso: Annotated[IObtenerTendenciaUseCase, Depends(container.obtener_tendencia)],
    meses: Meses = 12,
    hasta: str | None = None,
) -> Tendencia:
    """Gastos, ingresos y ahorro de los últimos `meses` (incluido el de `hasta`, por defecto el actual)."""
    dto = caso.ejecutar(ObtenerTendenciaInputDTO(hogar_id=hogar_id, meses=meses, hasta=hasta))
    return Tendencia.model_validate(dto, from_attributes=True)
