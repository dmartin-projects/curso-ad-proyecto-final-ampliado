"""El query service del dashboard con PostgreSQL (módulos 77 y 87): los números de un mes."""

from datetime import date
from decimal import Decimal

import pytest

from core.domain.vo.mes import Mes
from finanzas.domain.repositories.queries.dashboard_query import DashboardQuery
from finanzas.infrastructure.database.repositories.dashboard_query_service_orm import DashboardQueryServiceORM

pytestmark = pytest.mark.django_db
OCT = date(2026, 10, 1)


def test_calculo_del_mes(datos):
    hogar, _, comida, ocio = datos

    d = DashboardQueryServiceORM().resumen(DashboardQuery(hogar.pk, Mes.de(OCT)))  # un read model: atributos

    assert (d.gastos, d.ingresos, d.balance) == (Decimal("37.50"), Decimal("1000.00"), Decimal("962.50"))
    assert d.gastos_mes_anterior == Decimal("30.00") and d.variacion == Decimal("25.0")
    # la subcategoría Fruta suma en Comida
    assert [(c.nombre, c.total) for c in d.por_categoria] == [
        ("Ocio", Decimal("20")),
        ("Comida", Decimal("17.50")),
    ]
    assert [(f.fecha.day, f.gasto, f.acumulado) for f in d.acumulado] == [
        (1, Decimal("15.00"), Decimal("15.00")),
        (3, Decimal("20.00"), Decimal("35.00")),
        (7, Decimal("2.50"), Decimal("37.50")),
    ]
    assert len(d.evolucion) == 12 and d.evolucion[0].mes == date(2025, 11, 1)
    assert d.evolucion[0].gastos == 0 and d.evolucion[-2].gastos == Decimal("30.00")
    top = d.top_comercios[0]
    assert (top.nombre, top.total, top.veces) == ("Mercadona", Decimal("15.00"), 2)
    assert [(p.categoria, p.importe, p.gastado, p.porcentaje) for p in d.presupuestos] == [
        ("Comida", Decimal("10.00"), Decimal("17.50"), 175)
    ]
    assert d.pendientes_revision == 1
