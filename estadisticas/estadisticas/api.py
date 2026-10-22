# estadisticas/api.py — punto de entrada de la API: `uvicorn estadisticas.api:app` (el CMD del Dockerfile, módulo 85)
#
# El código está en infrastructure/api (módulo 89). Este archivo solo existe para que el comando no cambie.
from estadisticas.infrastructure.api.app import crear_app

app = crear_app()
