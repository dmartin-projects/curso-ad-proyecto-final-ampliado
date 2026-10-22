# estadisticas/infrastructure/api/exceptions/mes_mal_formado_handler.py — MesMalFormadoException → 422 (módulo 89)
#
# El exception handler de FastAPI que traduce una excepción del dominio a HTTP (en el monolito, el de DRF en
# core/infrastructure/api/exceptions). El único mes que llega de la API es el parámetro `hasta`.
from fastapi import Request, status
from fastapi.responses import JSONResponse

from estadisticas.domain.exceptions.mes_mal_formado_exception import MesMalFormadoException


async def mes_mal_formado(request: Request, exc: MesMalFormadoException) -> JSONResponse:
    return JSONResponse({"detail": "hasta: formato AAAA-MM"}, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
