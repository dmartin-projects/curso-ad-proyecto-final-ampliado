"""De qué meses se puede generar un informe (módulo 88), sin base de datos."""

from datetime import date

import pytest

from core.domain.vo.mes import Mes
from informes.domain.exceptions.mes_futuro_exception import MesFuturoException
from informes.domain.services.meses import comprobar_mes

HOY = date(2026, 10, 15)


def test_el_mes_en_curso_si_el_siguiente_no():
    assert comprobar_mes(Mes(2026, 10), HOY) == Mes(2026, 10)  # "lo que llevamos" de octubre
    with pytest.raises(MesFuturoException) as e:
        comprobar_mes(Mes(2026, 11), HOY)
    assert e.value.campo == "mes"
