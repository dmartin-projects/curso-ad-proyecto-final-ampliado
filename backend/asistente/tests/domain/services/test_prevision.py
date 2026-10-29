"""Módulo 95: la previsión de fin de mes, dos números y sus trampas (sin Django)."""

from datetime import date
from decimal import Decimal

from asistente.domain.read_models.gasto_del_dia import GastoDelDia
from asistente.domain.services.prevision import Prevision, acumulado_hasta, prever


def dias(*pares: tuple[str, str]) -> tuple[GastoDelDia, ...]:
    total, salida = Decimal(0), []
    for fecha, gasto in pares:
        total += Decimal(gasto)
        salida.append(GastoDelDia(date.fromisoformat(fecha), Decimal(gasto), total))
    return tuple(salida)


OCTUBRE = dias(("2026-10-02", "37.50"), ("2026-10-03", "301.25"), ("2026-10-18", "31.20"), ("2026-10-27", "71.40"))
SEPTIEMBRE = dias(("2026-09-02", "37.50"), ("2026-09-05", "287.90"), ("2026-09-28", "92.75"))


def test_al_ritmo_actual_y_el_mes_anterior_a_estas_alturas():
    p = prever(date(2026, 10, 20), OCTUBRE, SEPTIEMBRE)
    assert p == Prevision(
        gastado=Decimal("369.95"),  # hasta el día 20: no cuenta la luz del 27
        dias_transcurridos=20,
        dias_del_mes=31,
        al_ritmo_actual=Decimal("573.42"),  # 369,95 / 20 × 31
        mes_anterior_a_estas_alturas=Decimal("325.40"),
        mes_anterior_total=Decimal("418.15"),
    )


def test_el_31_frente_a_un_mes_de_30_dias_es_el_30():
    p = prever(date(2026, 10, 31), OCTUBRE, SEPTIEMBRE)
    assert p.mes_anterior_a_estas_alturas == Decimal("418.15")


def test_sin_mes_anterior_solo_el_ritmo():
    p = prever(date(2026, 10, 3), OCTUBRE, None)
    assert (p.gastado, p.al_ritmo_actual, p.mes_anterior_total) == (Decimal("338.75"), Decimal("3500.42"), None)


def test_un_dia_sin_gastos_es_el_acumulado_del_ultimo_que_tuvo():
    assert acumulado_hasta(OCTUBRE, 10) == Decimal("338.75")
    assert acumulado_hasta(OCTUBRE, 1) == Decimal("0")
