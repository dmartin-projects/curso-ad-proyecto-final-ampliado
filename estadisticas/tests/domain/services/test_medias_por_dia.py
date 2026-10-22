"""El domain service de las medias por día de la semana (módulo 89). Sin base de datos."""

from decimal import Decimal

from estadisticas.domain.services.medias_por_dia import gasto_medio_por_dia
from estadisticas.domain.vo.mes import Mes
from estadisticas.domain.vo.periodo import Periodo


def test_gasto_medio_por_dia():
    medias = gasto_medio_por_dia({2: Decimal("100"), 1: Decimal("40")}, Periodo.de_meses(Mes(2026, 9), 1))
    assert medias[:3] == [(1, "lunes", Decimal("10.00")), (2, "martes", Decimal("20.00")), (3, "miércoles", 0)]
