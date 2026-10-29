"""Módulo 95: el adapter de Frankfurter. Sin red (respx intercepta httpx) para los casos raros; con un cassette, contra
el servicio de verdad."""

from datetime import date
from decimal import Decimal

import httpx
import pytest
import respx

from asistente.domain.exceptions.moneda_desconocida_exception import MonedaDesconocidaException
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.read_models.conversion import Conversion
from asistente.infrastructure.externos.frankfurter_tipo_de_cambio import TipoDeCambioFrankfurter

URL = "https://api.frankfurter.dev/v1/"


def adapter() -> TipoDeCambioFrankfurter:
    return TipoDeCambioFrankfurter(base_url=URL, pausa=0)


@respx.mock
def test_convierte_y_guarda_el_tipo_de_una_fecha_pasada():
    ruta = respx.get(f"{URL}2026-09-12", params={"base": "GBP", "symbols": "EUR"}).respond(
        json={"amount": 1.0, "base": "GBP", "date": "2026-09-11", "rates": {"EUR": 1.1653}}
    )
    esperado = Conversion(Decimal("120"), "GBP", "EUR", Decimal("139.84"), Decimal("1.1653"), date(2026, 9, 11))

    assert adapter().convertir(Decimal("120"), "GBP", "EUR", date(2026, 9, 12)) == esperado
    assert adapter().convertir(Decimal("120"), "GBP", "EUR", date(2026, 9, 12)) == esperado
    assert ruta.call_count == 1  # la segunda, de la caché: el tipo de un día pasado no cambia


@respx.mock
def test_sin_fecha_el_ultimo():
    respx.get(f"{URL}latest").respond(
        json={"amount": 1.0, "base": "USD", "date": "2026-10-29", "rates": {"EUR": 0.8985}}
    )
    assert adapter().convertir(Decimal("10"), "USD", "EUR").resultado == Decimal("8.99")


def test_la_misma_moneda_ni_se_pregunta():
    assert adapter().convertir(Decimal("10"), "EUR", "EUR", date(2026, 9, 1)).tipo == Decimal(1)


@respx.mock
@pytest.mark.parametrize("status, cuerpo", [(404, {"message": "not found"}), (422, {"message": "bad currency pair"})])
def test_una_moneda_que_no_existe(status, cuerpo):
    respx.get(f"{URL}latest").respond(status, json=cuerpo)
    with pytest.raises(MonedaDesconocidaException):
        adapter().convertir(Decimal("1"), "XXX", "EUR")


@respx.mock
def test_un_5xx_se_reintenta_y_acaba_en_no_disponible():
    ruta = respx.get(f"{URL}latest").respond(503)
    with pytest.raises(ServicioExternoNoDisponibleException, match="Frankfurter .*: HTTP 503"):
        adapter().convertir(Decimal("1"), "USD", "EUR")
    assert ruta.call_count == 2


@respx.mock
def test_un_timeout_tambien():
    respx.get(f"{URL}latest").mock(side_effect=httpx.ReadTimeout("lento"))
    with pytest.raises(ServicioExternoNoDisponibleException, match="ReadTimeout"):
        adapter().convertir(Decimal("1"), "USD", "EUR")


@pytest.mark.vcr
def test_frankfurter_de_verdad():
    """Grabado el 29-10-2026: el 12 de septiembre de 2026 fue sábado, y el BCE da el tipo del viernes 11."""
    c = adapter().convertir(Decimal("120"), "GBP", "EUR", date(2026, 9, 12))
    assert (c.tipo, c.fecha_del_tipo, c.resultado) == (Decimal("1.1653"), date(2026, 9, 11), Decimal("139.84"))
