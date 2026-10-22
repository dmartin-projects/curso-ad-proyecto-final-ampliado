# estadisticas/infrastructure/api/v1/routers/dias_semana_router.py — GET /hogares/{hogar_id}/dias-semana (módulos 85
# y 89)
from typing import Annotated

from fastapi import APIRouter, Depends

from estadisticas.application.obtener_dias_semana_use_case.dtos.obtener_dias_semana_input_dto import (
    ObtenerDiasSemanaInputDTO,
)
from estadisticas.application.obtener_dias_semana_use_case.i_obtener_dias_semana_use_case import (
    IObtenerDiasSemanaUseCase,
)
from estadisticas.infrastructure import container
from estadisticas.infrastructure.api.dependencies.hogar_permitido import Hogar
from estadisticas.infrastructure.api.v1.parametros import Meses
from estadisticas.infrastructure.api.v1.schemas.dias_semana_schema import DiasSemana

router = APIRouter()


@router.get("/hogares/{hogar_id}/dias-semana", response_model=DiasSemana)
def dias_semana(
    hogar_id: Hogar,
    caso: Annotated[IObtenerDiasSemanaUseCase, Depends(container.obtener_dias_semana)],
    meses: Meses = 6,
    hasta: str | None = None,
) -> DiasSemana:
    """Cuánto se gasta de media cada día de la semana: total de ese día ÷ cuántos hubo en el periodo."""
    dto = caso.ejecutar(ObtenerDiasSemanaInputDTO(hogar_id=hogar_id, meses=meses, hasta=hasta))
    return DiasSemana.model_validate(dto, from_attributes=True)
