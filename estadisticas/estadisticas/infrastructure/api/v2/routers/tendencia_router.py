# estadisticas/infrastructure/api/v2/routers/tendencia_router.py — GET /hogares/{hogar_id}/tendencia de la v2
# (módulo 89, ejercicio 2)
#
# Reutiliza el use case y las dependencias de la v1 (mismo JWT, mismo 404) y añade la tasa de ahorro, una regla del
# dominio, con la forma de respuesta de la v2.
from typing import Annotated

from fastapi import APIRouter, Depends

from estadisticas.application.obtener_tendencia_use_case.dtos.obtener_tendencia_input_dto import (
    ObtenerTendenciaInputDTO,
)
from estadisticas.application.obtener_tendencia_use_case.i_obtener_tendencia_use_case import IObtenerTendenciaUseCase
from estadisticas.domain.services.ahorro import tasa_de_ahorro
from estadisticas.infrastructure import container
from estadisticas.infrastructure.api.dependencies.hogar_permitido import Hogar
from estadisticas.infrastructure.api.v1.parametros import Meses
from estadisticas.infrastructure.api.v2.schemas.mes_con_tasa_schema import MesConTasa
from estadisticas.infrastructure.api.v2.schemas.tendencia_con_tasa_schema import TendenciaConTasa

router = APIRouter()


@router.get("/hogares/{hogar_id}/tendencia", response_model=TendenciaConTasa)
def tendencia(
    hogar_id: Hogar,
    caso: Annotated[IObtenerTendenciaUseCase, Depends(container.obtener_tendencia)],
    meses: Meses = 12,
    hasta: str | None = None,
) -> TendenciaConTasa:
    """Como la v1, y además la tasa de ahorro de cada mes: qué % de los ingresos se ahorra."""
    dto = caso.ejecutar(ObtenerTendenciaInputDTO(hogar_id=hogar_id, meses=meses, hasta=hasta))
    return TendenciaConTasa(
        hogar_id=dto.hogar_id,
        ultimo_evento=dto.ultimo_evento,
        meses=[MesConTasa(**m.model_dump(), tasa_ahorro=tasa_de_ahorro(m.ingresos, m.ahorro)) for m in dto.meses],
    )
