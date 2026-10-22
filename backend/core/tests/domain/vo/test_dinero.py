"""El value object Dinero (módulo 87): sin base de datos, sin Django, en milisegundos."""

from decimal import Decimal

import pytest

from core.domain.vo.dinero import Dinero


def test_dinero_redondea_al_centimo_como_en_la_tienda():
    assert Dinero("10.005").cantidad == Decimal("10.01")  # ROUND_HALF_UP; con el de Decimal (al par): 10.00
    assert Dinero("-2.5") == Dinero(Decimal("-2.50"))  # value object: iguales por valor
    assert str(Dinero("-12.5")) == "-12.50"  # el mismo texto que el Decimal de la base de datos


def test_dinero_opera_y_no_acepta_float():
    assert Dinero("0.10") + Dinero("0.20") == Dinero("0.30")
    assert abs(Dinero("-110")) >= Dinero("100") and -Dinero("5") == Dinero("-5")
    assert Dinero("-1").es_gasto and Dinero.cero().es_cero
    with pytest.raises(TypeError):
        Dinero(0.1)
