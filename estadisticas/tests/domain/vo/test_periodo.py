"""El value object Periodo: qué meses entran, hasta qué día, cuántos de cada día (módulo 89). Sin base de datos."""

from datetime import date

from estadisticas.domain.vo.mes import Mes
from estadisticas.domain.vo.periodo import Periodo


def test_los_ultimos_meses_incluyen_los_vacios_y_cruzan_el_anio():
    periodo = Periodo.de_meses(Mes(2026, 2), 4)
    assert (periodo.desde, periodo.antes_de, periodo.hasta) == (date(2025, 11, 1), date(2026, 3, 1), date(2026, 2, 28))
    assert [str(m) for m in periodo.meses()] == ["2025-11", "2025-12", "2026-01", "2026-02"]


def test_el_mes_en_curso_solo_cuenta_hasta_hoy():
    hoy = date(2026, 10, 15)
    assert Periodo.de_meses_hasta_hoy(Mes(2026, 10), 1, hoy) == Periodo(date(2026, 10, 1), date(2026, 10, 16))
    assert Periodo.de_meses_hasta_hoy(Mes(2026, 9), 1, hoy).hasta == date(2026, 9, 30)  # un mes pasado, entero
    # un mes futuro cuenta como el actual: nunca un periodo que empiece después de terminar
    assert Periodo.de_meses_hasta_hoy(Mes(2027, 3), 2, hoy) == Periodo(date(2026, 9, 1), date(2026, 10, 16))


def test_cuantos_dias_de_cada():
    # Septiembre de 2026: empieza en martes y tiene 30 días → 5 martes y 5 miércoles, 4 de los demás
    assert Periodo.de_meses(Mes(2026, 9), 1).dias_de_la_semana() == {1: 4, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 4}
    assert sum(Periodo.de_meses(Mes(2026, 12), 12).dias_de_la_semana().values()) == 365
