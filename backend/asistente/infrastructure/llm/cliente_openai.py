# asistente/infrastructure/llm/cliente_openai.py — el cliente HTTP del SDK, uno por proceso (módulo 93)
import functools

import httpx2
from openai import OpenAI


@functools.lru_cache(maxsize=4)  # uno por configuración (en los tests cambian los ajustes)
def cliente_del_proceso(base_url: str, api_key: str, timeout: float) -> OpenAI:
    """Crear un cliente no es gratis (certificados, contexto TLS) y reutilizarlo mantiene la conexión abierta
    (keep-alive): cada llamada se ahorra el saludo TLS. Se crea en el primer uso, ya dentro del proceso (un worker de
    Celery, tras el fork).

    max_retries=0: los reintentos los decide el adapter (no todos los errores se reintentan igual: el 429).
    """
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=httpx2.Timeout(timeout, connect=5.0),  # por intento: conectar, 5 s; la respuesta entera, `timeout`
        max_retries=0,
    )
