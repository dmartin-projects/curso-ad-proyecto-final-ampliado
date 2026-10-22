"""Ejercicio 2: la tasa de ahorro. Sin base de datos."""

from decimal import Decimal

from estadisticas.domain.services.ahorro import tasa_de_ahorro


def test_tasa_de_ahorro():
    assert tasa_de_ahorro(Decimal("2000.00"), Decimal("500.00")) == Decimal("25.0")
    assert tasa_de_ahorro(Decimal("3"), Decimal("1")) == Decimal("33.3")
    assert tasa_de_ahorro(Decimal("1000"), Decimal("-250")) == Decimal("-25.0")  # se gasta más de lo que entra
    assert tasa_de_ahorro(Decimal("0"), Decimal("-50.50")) is None  # sin ingresos no hay tasa
