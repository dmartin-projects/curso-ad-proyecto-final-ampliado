# asistente/infrastructure/externos/eurostat_indice_de_precios.py — IIndiceDePrecios con Eurostat (IPC armonizado) (módulo 95)
"""El IPC armonizado (HICP) de España, por grupos COICOP 2018, de la API de difusión de Eurostat (JSON-stat, sin clave).
Es el mismo índice que publica el INE como IPCA; Eurostat lo ofrece por grupos en una API estable y documentada.

El patrón de una fuente de datos oficial y lenta:
- datos MENSUALES publicados con retraso (el IPC de septiembre sale a mediados de octubre): un mes que aún no está
  no es un cero, simplemente no aparece en la serie;
- caché larga (12 horas por grupo): la serie solo cambia cuando hay publicación nueva;
- timeout generoso (10 s): la API tarda; mejor una respuesta lenta que ninguna, pero nunca una pregunta colgada.
Los reintentos y el circuit breaker, los de ServicioHttp.
"""

from decimal import Decimal

import httpx
from django.core.cache import cache

from asistente.application.ports.i_indice_de_precios import IIndiceDePrecios
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.read_models.serie_de_precios import SerieDePrecios
from asistente.infrastructure.externos.servicio_http import ServicioHttp
from core.domain.vo.mes import Mes

SERVICIO = "Eurostat (IPC armonizado)"
DATASET = "prc_hicp_minr"  # HICP, ECOICOP ver. 2: índices y tasas de variación, mensual (el vigente desde 2026)
DOCE_HORAS = 12 * 3600


class IndiceDePreciosEurostat(IIndiceDePrecios):
    def __init__(self, *, base_url: str, timeout: float = 10.0, intentos: int = 2, pausa: float = 0.5):
        self.servicio = ServicioHttp(
            nombre=SERVICIO, clave="eurostat", base_url=base_url, timeout=timeout, intentos=intentos, pausa=pausa
        )

    def serie(self, grupo):
        clave = f"asistente:ipc:{grupo}"
        if (guardada := cache.get(clave)) is not None:
            return guardada
        parametros = {"geo": "ES", "unit": "RCH_A", "coicop18": grupo, "lastTimePeriod": 24}
        serie = _leer(grupo, self._pedir(DATASET, parametros))
        cache.set(clave, serie, timeout=DOCE_HORAS)
        return serie

    def _pedir(self, ruta: str, parametros: dict) -> dict:
        try:
            return self.servicio.get_json(ruta, parametros)
        except httpx.HTTPStatusError as e:  # un 4xx: la consulta ya no vale (un dataset retirado): no disponible
            raise ServicioExternoNoDisponibleException(SERVICIO, f"HTTP {e.response.status_code}") from e


def _leer(grupo: str, datos: dict) -> SerieDePrecios:
    """JSON-stat 2.0: los valores van en un objeto {posición: valor}, y la posición sale de las dimensiones. Con una
    sola serie (un grupo, una unidad, un país), la posición es la del mes en la dimensión `time`. Un mes sin valor
    (no publicado, o confidencial) no está en `value`."""
    meses = datos["dimension"]["time"]["category"]["index"]  # {"2026-09": 23, …}
    etiquetas = datos["dimension"]["coicop18"]["category"].get("label", {})
    valores = datos.get("value", {})
    tasas = {
        Mes.desde_texto(mes): Decimal(str(valores[str(posicion)]))
        for mes, posicion in meses.items()
        if str(posicion) in valores
    }
    return SerieDePrecios(grupo=grupo, nombre=etiquetas.get(grupo, grupo), tasas_anuales=tasas)
