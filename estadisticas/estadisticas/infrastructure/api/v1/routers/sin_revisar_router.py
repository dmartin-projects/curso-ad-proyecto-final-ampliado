# estadisticas/infrastructure/api/v1/routers/sin_revisar_router.py — GET /hogares/{hogar_id}/sin-revisar (módulo 85,
# ejercicio 4; aquí desde el 89)
from typing import Annotated

from fastapi import APIRouter, Depends

from estadisticas.application.obtener_sin_revisar_use_case.dtos.obtener_sin_revisar_input_dto import (
    ObtenerSinRevisarInputDTO,
)
from estadisticas.application.obtener_sin_revisar_use_case.i_obtener_sin_revisar_use_case import (
    IObtenerSinRevisarUseCase,
)
from estadisticas.infrastructure import container
from estadisticas.infrastructure.api.dependencies.hogar_permitido import Hogar
from estadisticas.infrastructure.api.v1.parametros import Meses
from estadisticas.infrastructure.api.v1.schemas.sin_revisar_schema import SinRevisar

router = APIRouter()


@router.get("/hogares/{hogar_id}/sin-revisar", response_model=SinRevisar)
def sin_revisar(
    hogar_id: Hogar,
    caso: Annotated[IObtenerSinRevisarUseCase, Depends(container.obtener_sin_revisar)],
    meses: Meses = 6,
    hasta: str | None = None,
) -> SinRevisar:
    """Cuántos movimientos (y cuánto gasto) quedan por revisar, mes a mes: lo que trajo la IA o el banco."""
    dto = caso.ejecutar(ObtenerSinRevisarInputDTO(hogar_id=hogar_id, meses=meses, hasta=hasta))
    return SinRevisar.model_validate(dto, from_attributes=True)
