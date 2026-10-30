# asistente/infrastructure/llm/cliente_anthropic.py — el cliente del SDK de Anthropic, uno por proceso (módulo 106)
import functools

import httpx2
from anthropic import Anthropic


@functools.lru_cache(maxsize=4)
def cliente_anthropic(api_key: str, timeout: float) -> Anthropic:
    """Como cliente_del_proceso (módulo 93): uno por proceso, con su conexión abierta. Aquí SÍ reintenta el SDK
    (max_retries=2, con espera exponencial y el retry-after de Anthropic): con Claude no hay una cuota diaria que
    distinguir de la por minuto, y un 529 (sobrecargado) se pasa en segundos. Lo que llega al adapter ya los ha
    agotado, y lo decide la reserva (módulo 94)."""
    return Anthropic(api_key=api_key, timeout=httpx2.Timeout(timeout, connect=5.0), max_retries=2)
