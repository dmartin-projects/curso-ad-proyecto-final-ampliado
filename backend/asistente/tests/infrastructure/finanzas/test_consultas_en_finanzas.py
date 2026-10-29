"""Módulo 94: el anti-corruption layer hacia finanzas y su fake cumplen el mismo contrato (contract tests)."""

from decimal import Decimal

import pytest

from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from asistente.infrastructure.finanzas.consultas_en_finanzas import ConsultasEnFinanzas
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
