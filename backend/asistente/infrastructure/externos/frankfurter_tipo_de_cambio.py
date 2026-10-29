# asistente/infrastructure/externos/frankfurter_tipo_de_cambio.py — ITipoDeCambio con Frankfurter (tipos del BCE) (módulo 95)
"""Frankfurter (frankfurter.dev) publica, sin clave, los tipos de referencia del Banco Central Europeo: uno por día
laborable, hacia las 16:00 CET. Una API de terceros, con sus reglas:

- timeout corto, reintentos de lo transitorio y circuit breaker: los de ServicioHttp, como todos los servicios externos;
- caché: el tipo de una fecha pasada no cambia nunca (30 días en Redis); el último, como mucho una hora;
- sus errores, traducidos: una moneda que no existe es un error del usuario (MonedaDesconocidaException); que no
  responda, ServicioExternoNoDisponibleException. La tool decide qué le dice al modelo.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import httpx
from django.core.cache import cache

from asistente.application.ports.i_tipo_de_cambio import ITipoDeCambio
from asistente.domain.exceptions.moneda_desconocida_exception import MonedaDesconocidaException
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.read_models.conversion import Conversion
from asistente.infrastructure.externos.servicio_http import ServicioHttp

SERVICIO = "Frankfurter (tipos de cambio del BCE)"
UN_MES, UNA_HORA = 30 * 24 * 3600, 3600


CENTIMO = Decimal("0.01")  # redondeo "como en la tienda", el mismo que Dinero


class TipoDeCambioFrankfurter(ITipoDeCambio):
    def __init__(self, *, base_url: str, timeout: float = 5.0, intentos: int = 2, pausa: float = 0.3):
        self.servicio = ServicioHttp(
            nombre=SERVICIO, clave="frankfurter", base_url=base_url, timeout=timeout, intentos=intentos, pausa=pausa
        )

    def convertir(self, importe, de, a, fecha=None):
        if de == a:
            return Conversion(importe, de, a, importe, Decimal(1), fecha or date.today())
        tipo, fecha_del_tipo = self._tipo(de, a, fecha)
        return Conversion(
            importe, de, a, (importe * tipo).quantize(CENTIMO, rounding=ROUND_HALF_UP), tipo, fecha_del_tipo
        )

    def _tipo(self, de: str, a: str, fecha: date | None) -> tuple[Decimal, date]:
        clave = f"asistente:tipo_de_cambio:{fecha or 'ultimo'}:{de}:{a}"
        if (guardado := cache.get(clave)) is not None:
            return Decimal(guardado[0]), date.fromisoformat(guardado[1])
        datos = self._pedir(fecha.isoformat() if fecha else "latest", {"base": de, "symbols": a})
        tipo, fecha_del_tipo = Decimal(str(datos["rates"][a])), date.fromisoformat(datos["date"])
        cache.set(clave, (str(tipo), fecha_del_tipo.isoformat()), timeout=UN_MES if fecha else UNA_HORA)
        return tipo, fecha_del_tipo

    def _pedir(self, ruta: str, parametros: dict) -> dict:
        try:
            return self.servicio.get_json(ruta, parametros)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 422):  # "not found" / "bad currency pair": una moneda que no publica
                raise MonedaDesconocidaException() from e
            raise ServicioExternoNoDisponibleException(SERVICIO, f"HTTP {e.response.status_code}") from e
