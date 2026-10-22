# estadisticas/infrastructure/api/v2/router.py — la versión 2 de la API (módulo 89, ejercicio 2)
from fastapi import APIRouter

from estadisticas.infrastructure.api.v2.routers import tendencia_router

router = APIRouter()
router.include_router(tendencia_router.router)
