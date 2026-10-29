"""Módulo 95: cuántos movimientos cumplen unos filtros y cuánto suman, en una consulta (lo pide el asistente)."""

from datetime import date
from decimal import Decimal

import pytest

from conftest import CategoriaFactory, CuentaFactory, MovimientoFactory
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from finanzas.application.obtener_totales_movimientos_use_case.dtos.obtener_totales_movimientos_input_dto import (
    ObtenerTotalesMovimientosInputDTO,
)
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery
from finanzas.infrastructure import container
from finanzas.models import Comercio


@pytest.fixture
def hogar(hogar_con_roles):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    comida = CategoriaFactory(hogar=hogar, nombre="Comida")
    fruta = CategoriaFactory(hogar=hogar, nombre="Fruta", padre=comida)
    mercadona = Comercio.objects.create(nombre="Mercadona")
    for fecha, importe, categoria, comercio in [
        ("2026-09-01", "-10.00", comida, mercadona),
        ("2026-09-02", "-5.50", fruta, mercadona),
        ("2026-09-03", "-20.00", None, None),
        ("2026-09-05", "1000.00", None, None),
        ("2026-10-01", "-7.25", comida, mercadona),
    ]:
        MovimientoFactory(
            cuenta=cuenta, fecha=date.fromisoformat(fecha), importe=Decimal(importe), categoria=categoria,
            comercio=comercio, concepto="Compra" if comercio else "Otro",
        )  # fmt: skip
    otro = CuentaFactory()  # otro hogar: nunca suma
    MovimientoFactory(cuenta=otro, fecha=date(2026, 9, 1), importe=Decimal("-999"))
    return hogar, roles, comida


def totales(hogar, actor, **filtros):
    entrada = ObtenerTotalesMovimientosInputDTO(hogar.pk, actor, FiltrosMovimientosQuery(**filtros))
    return container.obtener_totales_movimientos().ejecutar(entrada)


def test_suma_gastos_e_ingresos_de_los_filtrados(hogar):
    h, roles, comida = hogar
    lector = Actor(roles["lector"].pk, Rol.LECTOR)
    septiembre = {"fecha_desde": date(2026, 9, 1), "fecha_hasta": date(2026, 9, 30)}

    t = totales(h, lector, **septiembre)
    assert (t.num, t.gastos, t.ingresos) == (4, Decimal("35.50"), Decimal("1000.00"))
    # una categoría principal incluye sus subcategorías, como en el listado
    t = totales(h, lector, categorias=(comida.pk,))
    assert (t.num, t.gastos, t.ingresos) == (3, Decimal("22.75"), Decimal("0"))
    t = totales(h, lector, busqueda=("mercadona",), tipo="gasto", **septiembre)
    assert (t.num, t.gastos) == (2, Decimal("15.50"))


def test_sin_resultados_a_cero(hogar):
    h, roles, _ = hogar
    t = totales(h, Actor(roles["lector"].pk, Rol.LECTOR), fecha_desde=date(2030, 1, 1))
    assert (t.num, t.gastos, t.ingresos) == (0, Decimal("0"), Decimal("0"))
