"""El value object Mes (módulo 89). Sin base de datos."""

from datetime import date

import pytest

from estadisticas.domain.exceptions.mes_mal_formado_exception import MesMalFormadoException
from estadisticas.domain.vo.mes import Mes


def test_mes():
    assert Mes.desde_texto("2026-10") == Mes(2026, 10) == Mes.de(date(2026, 10, 31))
    assert str(Mes(2026, 1).mas(-1)) == "2025-12"
    assert Mes(2025, 12).mas(1) == Mes(2026, 1) and Mes(2026, 3).mas(-14) == Mes(2025, 1)
    assert Mes(2026, 2) < Mes(2026, 10)


@pytest.mark.parametrize("texto", ["octubre", "2026-13", "2026/10", ""])
def test_mes_mal_formado(texto):
    with pytest.raises(MesMalFormadoException):
        Mes.desde_texto(texto)
