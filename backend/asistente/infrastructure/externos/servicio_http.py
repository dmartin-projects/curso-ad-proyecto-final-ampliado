# asistente/infrastructure/externos/servicio_http.py — lo común a los servicios externos de las tools (módulo 95)
"""Un servicio HTTP de terceros, con las reglas de siempre en un solo sitio:

- timeout corto: si no responde en unos segundos, la pregunta no puede esperar;
- reintentos acotados, solo de lo transitorio (red y 5xx), con backoff y jitter: un 404 no va a existir en un segundo;
- un circuit breaker por servicio (el de core, con el estado en Redis: lo comparten todos los procesos). Tres
  preguntas seguidas sin respuesta y el servicio descansa un minuto: las siguientes ni lo intentan, y el agente no
  paga en cada una dos intentos y un timeout;
- lo que no es un dato, traducido: un fallo del servicio (red, 5xx, circuito abierto) sale como
  ServicioExternoNoDisponibleException; un 4xx sale como httpx.HTTPStatusError, porque solo el adapter sabe qué
  significa (para Frankfurter, un 404 es una moneda que no existe: un error del usuario, que no abre el circuito).
"""

from typing import Any

import httpx
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential_jitter

from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from core.infrastructure.cache.circuito_abierto_exception import CircuitoAbiertoException


class ServicioHttp:
    def __init__(
        self,
        *,
        nombre: str,  # para los mensajes: "Frankfurter (tipos de cambio del BCE)"
        clave: str,  # para el circuit breaker: "frankfurter"
        base_url: str,
        timeout: float,
        intentos: int = 2,
        pausa: float = 0.3,
        umbral: int = 3,
        enfriamiento: int = 60,
    ):
        self.nombre = nombre
        self.http = httpx.Client(base_url=base_url, timeout=httpx.Timeout(timeout, connect=3.0))
        self.intentos, self.pausa = intentos, pausa
        self.circuito = CircuitBreaker(f"externo:{clave}", umbral=umbral, enfriamiento=enfriamiento)

    def get_json(self, ruta: str, parametros: dict | None = None) -> Any:
        try:
            respuesta = self.circuito.llamar(self._pedir, ruta, parametros)
        except CircuitoAbiertoException as e:  # ha fallado hace poco: ni se intenta
            raise ServicioExternoNoDisponibleException(self.nombre, "no responde desde hace un rato") from e
        except httpx.HTTPStatusError as e:  # un 5xx tras los reintentos
            raise ServicioExternoNoDisponibleException(self.nombre, f"HTTP {e.response.status_code}") from e
        except httpx.TransportError as e:  # timeout, conexión rechazada, DNS…
            raise ServicioExternoNoDisponibleException(self.nombre, type(e).__name__) from e
        respuesta.raise_for_status()  # un 4xx: el adapter decide qué significa
        return respuesta.json()

    def _pedir(self, ruta: str, parametros: dict | None) -> httpx.Response:
        """Solo los fallos del SERVICIO salen como excepción y cuentan para el circuit breaker; un 4xx se devuelve
        como respuesta (es culpa de la petición, no del servicio)."""
        for intento in Retrying(
            stop=stop_after_attempt(self.intentos),
            wait=wait_exponential_jitter(multiplier=self.pausa, max=3, jitter=self.pausa),
            retry=retry_if_exception(_transitorio),
            reraise=True,
        ):
            with intento:
                respuesta = self.http.get(ruta, params=parametros)
                if respuesta.status_code >= 500:
                    respuesta.raise_for_status()
        return respuesta


def _transitorio(e: BaseException) -> bool:
    if isinstance(e, httpx.TransportError):
        return True
    return isinstance(e, httpx.HTTPStatusError) and e.response.status_code >= 500
