"""El value object Mes (módulo 87)."""

from datetime import date

import pytest

from core.domain.vo.mes import Mes


@pytest.mark.parametrize(
    "mes, anterior, siguiente",
    [(Mes(2026, 1), Mes(2025, 12), Mes(2026, 2)), (Mes(2026, 12), Mes(2026, 11), Mes(2027, 1))],
)
def test_mes_cambia_de_anio(mes, anterior, siguiente):
    assert (mes.anterior(), mes.siguiente()) == (anterior, siguiente)


def test_mes_rango_y_texto():
    octubre = Mes.de(date(2026, 10, 31))
    assert (octubre.inicio, octubre.fin) == (date(2026, 10, 1), date(2026, 11, 1))
    assert octubre.contiene(date(2026, 10, 31)) and not octubre.contiene(date(2026, 11, 1))
    assert str(octubre) == "2026-10" and Mes.desde_texto("2026-10") == octubre
    assert octubre.ultimos(3) == [Mes(2026, 8), Mes(2026, 9), octubre]
    with pytest.raises(ValueError):
        Mes(2026, 13)
