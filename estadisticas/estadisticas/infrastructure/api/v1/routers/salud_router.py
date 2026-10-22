# estadisticas/infrastructure/api/v1/routers/salud_router.py — GET /salud, para el healthcheck del Dockerfile
# (módulos 85 y 89). Fuera del esquema OpenAPI.
from typing import Annotated

from fastapi import APIRouter, Depends

from estadisticas.domain.repositories.i_progreso_query_service import IProgresoQueryService
from estadisticas.infrastructure import container
from estadisticas.infrastructure.container import Sesion
from estadisticas.infrastructure.database.conexion import comprobar_conexion

router = APIRouter()


@router.get("/salud", include_in_schema=False)
def salud(s: Sesion, progreso: Annotated[IProgresoQueryService, Depends(container.progreso_query_service)]) -> dict:
    comprobar_conexion(s)
    return {"bd": "ok", "ultimo_evento": progreso.ultimo_evento()}
