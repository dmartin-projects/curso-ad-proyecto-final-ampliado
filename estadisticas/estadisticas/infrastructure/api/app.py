# estadisticas/infrastructure/api/app.py — la aplicación FastAPI: el router principal (módulos 85 y 89)
#
# Como config/api_v1.py en el monolito, solo MONTA: la telemetría, cada versión de la API con su prefijo y los
# exception handlers. Ni un endpoint.
from fastapi import FastAPI

from estadisticas.domain.exceptions.mes_mal_formado_exception import MesMalFormadoException
from estadisticas.infrastructure.api.exceptions.mes_mal_formado_handler import mes_mal_formado
from estadisticas.infrastructure.api.v1.router import router as v1
from estadisticas.infrastructure.metrics.retraso_consumidor import registrar_metrica
from estadisticas.infrastructure.telemetry import telemetria


def crear_app() -> FastAPI:
    if telemetria.configurar("estadisticas-api"):
        registrar_metrica()  # módulo 85, ejercicio 2: el retraso del consumidor, medido desde la API
    app = FastAPI(
        title="Estadísticas de Gastos",
        version="1.0",
        docs_url="/estadisticas/docs",
        openapi_url="/estadisticas/openapi.json",
    )
    # El mismo prefijo en desarrollo y detrás de Caddy: sin reescribir rutas. Una v2 sería otro router en api/v2
    app.include_router(v1, prefix="/estadisticas/v1")
    app.add_exception_handler(MesMalFormadoException, mes_mal_formado)
    telemetria.instrumentar_api(app)
    return app
