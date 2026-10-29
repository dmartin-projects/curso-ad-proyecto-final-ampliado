# asistente/infrastructure/externos/nager_festivos.py — IFestivos con Nager.Date (módulo 95, ejercicio 1)
"""Nager.Date (date.nager.at) publica, sin clave, los festivos oficiales de unos cien países: los nacionales y los
regionales, NO los locales de cada municipio. El mismo patrón que Frankfurter: ServicioHttp (timeout corto, reintentos
de lo transitorio, circuit breaker), caché (el calendario de un año casi no cambia: un día) y los fallos traducidos a
ServicioExternoNoDisponibleException."""

from datetime import date

import httpx
from django.core.cache import cache

from asistente.application.ports.i_festivos import IFestivos
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.read_models.festivo import Festivo
from asistente.infrastructure.externos.servicio_http import ServicioHttp

SERVICIO = "Nager.Date (festivos)"
UN_DIA = 24 * 3600


class FestivosNager(IFestivos):
    def __init__(self, *, base_url: str, timeout: float = 5.0, intentos: int = 2, pausa: float = 0.3):
        self.servicio = ServicioHttp(
            nombre=SERVICIO, clave="nager", base_url=base_url, timeout=timeout, intentos=intentos, pausa=pausa
        )

    def del_anio(self, anio, pais):
        clave = f"asistente:festivos:{pais}:{anio}"
        if (guardados := cache.get(clave)) is not None:
            return guardados
        festivos = tuple(
            Festivo(date.fromisoformat(x["date"]), x["localName"], tuple(x["counties"] or ()))
            for x in self._pedir(f"PublicHolidays/{anio}/{pais}")
            if "Public" in x["types"]  # los días de banco o de escuela no son festivos para todos
        )
        cache.set(clave, festivos, timeout=UN_DIA)
        return festivos

    def _pedir(self, ruta: str) -> list[dict]:
        try:
            return self.servicio.get_json(ruta)
        except httpx.HTTPStatusError as e:  # un 4xx: un país o un año que no publica
            raise ServicioExternoNoDisponibleException(SERVICIO, f"HTTP {e.response.status_code}") from e
