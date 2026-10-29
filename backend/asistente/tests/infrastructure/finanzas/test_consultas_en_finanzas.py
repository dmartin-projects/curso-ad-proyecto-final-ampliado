"""Módulo 94: el anti-corruption layer hacia finanzas y su fake cumplen el mismo contrato (contract tests)."""

from datetime import date
from decimal import Decimal

import pytest

from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from asistente.domain.vo.filtro_de_movimientos import FiltroDeMovimientos
from asistente.infrastructure.finanzas.consultas_en_finanzas import ConsultasEnFinanzas
from asistente.tests.fakes import casa as datos
from asistente.tests.fakes.consultas_de_finanzas_fake import ConsultasDeFinanzasFake, resumen
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes

SEPTIEMBRE = Mes(2026, 9)


@pytest.fixture(params=["fake", "orm"])
def finanzas(request, casa):
    ana, hogar = casa
    if request.param == "orm":
        return ConsultasEnFinanzas(), ana, hogar
    datos = resumen(
        SEPTIEMBRE,
        gastos="776.59",
        ingresos="2100.00",
        num=10,
        anterior="671.35",
        categorias=[
            ("Supermercado", "461.35"),
            ("Restaurantes", "102.00"),
            ("Casa", "92.75"),
            ("Ocio", "82.99"),
            ("Transporte", "37.50"),
        ],
    )
    return ConsultasDeFinanzasFake({(hogar.pk, SEPTIEMBRE): datos}), ana, hogar


def test_resumen_del_mes(finanzas):
    consultas, ana, hogar = finanzas
    r = consultas.resumen_del_mes(Actor(ana.pk, Rol.LECTOR), hogar.pk, SEPTIEMBRE)

    assert (r.mes, r.gastos, r.ingresos, r.balance) == (
        SEPTIEMBRE,
        Decimal("776.59"),
        Decimal("2100.00"),
        Decimal("1323.41"),
    )
    assert (r.num_movimientos, r.gastos_mes_anterior, r.variacion) == (10, Decimal("671.35"), Decimal("15.7"))
    assert r.por_categoria[:2] == (
        GastoDeCategoria("Supermercado", Decimal("461.35"), Decimal("59.4")),
        GastoDeCategoria("Restaurantes", Decimal("102.00"), Decimal("13.1")),
    )
    assert [c.categoria for c in r.por_categoria] == ["Supermercado", "Restaurantes", "Casa", "Ocio", "Transporte"]


def test_un_mes_sin_movimientos_a_cero(finanzas):
    consultas, ana, hogar = finanzas
    r = consultas.resumen_del_mes(Actor(ana.pk, Rol.LECTOR), hogar.pk, Mes(2025, 1))
    assert (r.gastos, r.num_movimientos, r.por_categoria) == (Decimal("0"), 0, ())


@pytest.fixture(params=["fake", "orm"])
def de_casa(request, casa):
    ana, hogar = casa
    consultas = ConsultasEnFinanzas() if request.param == "orm" else ConsultasDeFinanzasFake.de_casa(hogar.pk)
    return consultas, Actor(ana.pk, Rol.LECTOR), hogar


def test_movimientos_totales_de_todos_y_los_mas_recientes(de_casa):
    consultas, lector, hogar = de_casa
    filtro = FiltroDeMovimientos(date(2026, 8, 1), date(2026, 10, 29), texto="mercadona")
    r = consultas.movimientos(lector, hogar.pk, filtro, limite=2)
    assert (r.total, r.gastos, r.ingresos) == (5, Decimal("1121.05"), Decimal("0"))
    assert [(m.fecha, m.importe, m.categoria, m.comercio) for m in r.primeros] == [
        (date(2026, 10, 3), Decimal("-301.25"), "Supermercado", "Mercadona"),
        (date(2026, 9, 19), Decimal("-121.35"), "Supermercado", "Mercadona"),
    ]


def test_movimientos_de_una_categoria_principal_con_sus_hijas(de_casa):
    consultas, lector, hogar = de_casa
    casa_ = next(c for c in consultas.categorias(lector, hogar.pk) if c.nombre == "Casa")
    filtro = FiltroDeMovimientos(date(2025, 9, 1), date(2026, 10, 29), categoria_id=casa_.id, tipo="gasto")
    r = consultas.movimientos(lector, hogar.pk, filtro, limite=0)
    assert (r.total, r.gastos, r.primeros) == (4, Decimal("332.25"), ())


def test_categorias_con_su_principal(de_casa):
    consultas, lector, hogar = de_casa
    categorias = consultas.categorias(lector, hogar.pk)
    assert [(c.nombre, c.padre, c.es_ingreso) for c in categorias] == sorted(datos.CATEGORIAS)  # y en el mismo orden


def test_el_resto_del_dashboard(casa):
    """Lo que el 95 añade al resumen: solo el adapter (el fake devuelve lo que el test le da)."""
    ana, hogar = casa
    r = ConsultasEnFinanzas().resumen_del_mes(Actor(ana.pk, Rol.LECTOR), hogar.pk, SEPTIEMBRE)
    assert [(c.comercio, c.total, c.veces) for c in r.top_comercios][:2] == [
        ("Mercadona", Decimal("409.25"), 2),
        ("Lidl", Decimal("52.10"), 1),
    ]
    assert (r.evolucion[0].mes, len(r.evolucion)) == (Mes(2025, 10), 12)  # 12 meses, también los vacíos
    assert [(m.mes, m.gastos) for m in r.evolucion if m.gastos] == [
        (Mes(2026, 8), Decimal("671.35")),
        (Mes(2026, 9), Decimal("776.59")),
    ]
    assert (r.por_dia[0].fecha, r.por_dia[-1].acumulado) == (date(2026, 9, 2), Decimal("776.59"))
    assert r.presupuestos == ()
