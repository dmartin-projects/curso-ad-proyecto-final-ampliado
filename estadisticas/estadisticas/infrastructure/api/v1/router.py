# estadisticas/infrastructure/api/v1/router.py — la versión 1 de la API: lo que consulta Angular (módulos 85 y 89)
#
# El equivalente del urls.py de una app de Django: reúne los routers de routers/ (uno por endpoint) y nada más.
# app.py lo monta con su prefijo.
from fastapi import APIRouter

from estadisticas.infrastructure.api.v1.routers import (
    dias_semana_router,
    salud_router,
    sin_revisar_router,
    tendencia_router,
)

router = APIRouter()
router.include_router(salud_router.router)
router.include_router(tendencia_router.router)
router.include_router(dias_semana_router.router)
router.include_router(sin_revisar_router.router)
