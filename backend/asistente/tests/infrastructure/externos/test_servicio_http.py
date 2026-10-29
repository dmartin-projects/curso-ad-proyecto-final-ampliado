"""Módulo 95: lo común a los servicios externos. Reintentos de lo transitorio y un circuit breaker por servicio, sin red
(respx) y con la caché de los tests (locmem, vacía en cada test)."""

import httpx
import pytest
import respx

from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.infrastructure.externos.servicio_http import ServicioHttp

URL = "https://servicio.example/"


def servicio(clave: str = "prueba") -> ServicioHttp:
    return ServicioHttp(nombre="Un servicio", clave=clave, base_url=URL, timeout=1.0, pausa=0)


@respx.mock
def test_tres_preguntas_sin_respuesta_y_la_cuarta_ni_sale():
    ruta = respx.get(f"{URL}datos").mock(side_effect=httpx.ConnectError("caído"))
    s = servicio()
    for _ in range(3):
        with pytest.raises(ServicioExternoNoDisponibleException, match="ConnectError"):
            s.get_json("datos")
    assert ruta.call_count == 6  # dos intentos por pregunta

    with pytest.raises(ServicioExternoNoDisponibleException, match="no responde desde hace un rato"):
        s.get_json("datos")
    assert ruta.call_count == 6  # con el circuito abierto, ni una petición más


@respx.mock
def test_un_4xx_no_es_culpa_del_servicio():
    """Una moneda que no existe, cien veces: el servicio sigue disponible para las demás preguntas."""
    ruta = respx.get(f"{URL}datos").respond(404, json={"message": "not found"})
    s = servicio()
    for _ in range(4):
        with pytest.raises(httpx.HTTPStatusError):
            s.get_json("datos")
    assert ruta.call_count == 4  # ni se reintenta ni abre el circuito


@respx.mock
def test_un_acierto_pone_la_cuenta_a_cero():
    ruta = respx.get(f"{URL}datos")
    ruta.side_effect = [httpx.Response(503), httpx.Response(503), httpx.Response(200, json={"ok": True})] * 2
    s = servicio()
    with pytest.raises(ServicioExternoNoDisponibleException, match="HTTP 503"):
        s.get_json("datos")  # dos 503: un fallo
    assert s.get_json("datos") == {"ok": True}  # el reintento acierta: la cuenta vuelve a cero
    assert not s.circuito.abierto


@respx.mock
def test_cada_servicio_tiene_su_circuito():
    respx.get(f"{URL}datos").mock(side_effect=httpx.ConnectError("caído"))
    uno, otro = servicio("uno"), servicio("otro")
    for _ in range(3):
        with pytest.raises(ServicioExternoNoDisponibleException):
            uno.get_json("datos")
    assert uno.circuito.abierto and not otro.circuito.abierto
