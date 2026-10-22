import json
from datetime import date
from decimal import Decimal

import httpx
import pytest

from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from core.infrastructure.cache.circuito_abierto_exception import CircuitoAbiertoException
from tickets.infrastructure.ia.cliente_ia import ClienteIA
from tickets.infrastructure.ia.respuesta_ia_exception import RespuestaIAException
from tickets.infrastructure.ia.transitorio_ia_exception import TransitorioIAException
from tickets.tests.conftest import URL_IA, datos_ia, respuesta_ia


@pytest.fixture
def cliente():
    with ClienteIA(base_url="https://ia.test/v1/", api_key="k", modelo="m") as c:
        yield c


def test_envia_esquema_con_las_categorias_del_hogar_y_valida_la_respuesta(cliente, respx_mock):
    ruta = respx_mock.post(URL_IA).mock(return_value=respuesta_ia(datos_ia()))

    datos = cliente.extraer_ticket("MERCADONA…", ["Supermercado", "Ocio"])

    cuerpo = json.loads(ruta.calls.last.request.content)
    assert ruta.calls.last.request.headers["Authorization"] == "Bearer k"
    esquema = cuerpo["response_format"]["json_schema"]["schema"]
    assert esquema["properties"]["categoria"]["enum"] == ["Supermercado", "Ocio", ""]
    assert cuerpo["temperature"] == 0
    assert len(cuerpo["messages"][1]["content"]) == 1  # sin imagen
    assert datos["total"] == Decimal("4.85") and datos["fecha"] == date(2026, 10, 12)
    assert datos["lineas"][0]["cantidad"] == Decimal("2.000")


def test_si_el_ocr_no_sirve_envia_la_imagen(cliente, respx_mock):
    ruta = respx_mock.post(URL_IA).mock(return_value=respuesta_ia(datos_ia()))
    cliente.extraer_ticket("", ["Ocio"], imagen_png=b"\x89PNG...")
    parte = json.loads(ruta.calls.last.request.content)["messages"][1]["content"][1]
    assert parte["type"] == "image_url" and parte["image_url"]["url"].startswith("data:image/png;base64,")


def test_normaliza_lo_que_devuelve_la_ia(cliente, respx_mock):
    respx_mock.post(URL_IA).mock(return_value=respuesta_ia(datos_ia(fecha="", total=4.849999)))
    datos = cliente.extraer_ticket("…", [])
    assert datos["fecha"] is None
    assert datos["total"] == Decimal("4.85")  # redondeado, no rechazado


@pytest.mark.parametrize(
    "respuesta, error",
    [
        (httpx.Response(429), TransitorioIAException),
        (httpx.Response(503), TransitorioIAException),
        (httpx.ConnectTimeout("lento"), TransitorioIAException),
        (httpx.Response(401, json={"error": "clave"}), RespuestaIAException),
        (httpx.Response(200, json={"choices": [{"message": {"content": "no es json"}}]}), RespuestaIAException),
        (respuesta_ia(datos_ia(total=-3)), RespuestaIAException),  # el total no puede ser negativo
        (respuesta_ia(datos_ia(confianza=7)), RespuestaIAException),
    ],
)
def test_clasifica_los_errores(cliente, respx_mock, respuesta, error):
    ruta = respx_mock.post(URL_IA)
    if isinstance(respuesta, Exception):
        ruta.mock(side_effect=respuesta)
    else:
        ruta.mock(return_value=respuesta)
    with pytest.raises(error):
        cliente.extraer_ticket("…", [])


def test_circuit_breaker_deja_de_llamar_tras_el_umbral():
    llamadas = []

    def falla():
        llamadas.append(1)
        raise TransitorioIAException("503")

    breaker = CircuitBreaker("prueba", umbral=3, enfriamiento=60)
    for _ in range(3):
        with pytest.raises(TransitorioIAException):
            breaker.llamar(falla)
    with pytest.raises(CircuitoAbiertoException):
        breaker.llamar(falla)
    assert len(llamadas) == 3


def test_el_cliente_de_la_ia_se_reutiliza_en_el_proceso():
    with ClienteIA.desde_settings() as primero:
        pass
    with ClienteIA.desde_settings() as segundo:
        assert segundo is primero  # el mismo httpx.Client: sus conexiones abiertas se reutilizan
        assert not segundo._http.is_closed  # salir del with no cierra el del proceso
