"""Contract test de IGastos (módulo 88): el adapter hacia finanzas y su fake se portan igual."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from conftest import CategoriaFactory, CuentaFactory
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from finanzas.models import Movimiento as MovimientoModel
from tickets.application.ports.i_gastos import IGastos
from tickets.infrastructure.finanzas.gastos_en_finanzas import GastosEnFinanzas
from tickets.tests.fakes.gastos_fake import GastosFake
from tickets.tests.fakes.mundo import HOGAR, OTRO_HOGAR


@dataclass
class Entorno:
    gastos: IGastos
    hogar: int
    otro_hogar: int
    cuenta: int
    leer_gasto: object  # id → {"total", "concepto", "revisado"}


@pytest.fixture(params=["memoria", "orm"])
def entorno(request) -> Entorno:
    if request.param == "memoria":
        gastos = GastosFake((HOGAR, 10))

        def leer(pk):
            g = gastos.gastos.get(pk)
            return None if g is None else {k: g[k] for k in ("total", "concepto", "revisado")}

        return Entorno(gastos, HOGAR, OTRO_HOGAR, 10, leer)
    request.getfixturevalue("db")
    cuenta, ajena = CuentaFactory(), CuentaFactory()
    CategoriaFactory(hogar=cuenta.hogar, nombre="Supermercado")

    def leer(pk):
        m = MovimientoModel.objects.filter(pk=pk).first()
        return None if m is None else {"total": -m.importe, "concepto": m.concepto, "revisado": m.revisado}

    return Entorno(GastosEnFinanzas(), cuenta.hogar_id, ajena.hogar_id, cuenta.pk, leer)


def test_gastos_apuntar_corregir_y_descartar(entorno):
    g, sistema, ana = entorno.gastos, Actor.sistema(en_nombre_de=None), Actor(None, Rol.MIEMBRO)
    assert "Supermercado" in g.nombres_de_categorias(entorno.hogar)
    assert g.existe_cuenta(entorno.hogar, entorno.cuenta) and not g.existe_cuenta(entorno.otro_hogar, entorno.cuenta)
    comun = {"hogar_id": entorno.hogar, "cuenta_id": entorno.cuenta, "fecha": date(2026, 10, 12)}
    propuesto = g.apuntar(
        actor=sistema,
        total=Decimal("4.85"),
        concepto="Mercadona",
        comercio="Mercadona",
        nif="",
        categoria_sugerida="",
        revisado=False,
        **comun,
    )
    revisado = g.apuntar(
        actor=sistema,
        total=Decimal("1"),
        concepto="Bar",
        comercio="",
        nif="",
        categoria_sugerida="",
        revisado=True,
        **comun,
    )
    assert entorno.leer_gasto(propuesto) == {"total": Decimal("4.85"), "concepto": "Mercadona", "revisado": False}

    assert g.descartar(hogar_id=entorno.hogar, actor=ana, movimiento_id=revisado) is False  # ya revisado: no
    assert g.descartar(hogar_id=entorno.hogar, actor=ana, movimiento_id=propuesto) is True
    assert entorno.leer_gasto(propuesto) is None and entorno.leer_gasto(revisado) is not None

    g.corregir(
        hogar_id=entorno.hogar,
        actor=ana,
        movimiento_id=revisado,
        fecha=date(2026, 10, 12),
        total=Decimal("2.50"),
        concepto="Bar Manolo",
        categoria_id=None,
    )
    assert entorno.leer_gasto(revisado) == {"total": Decimal("2.50"), "concepto": "Bar Manolo", "revisado": True}
    nuevo_id = g.registrar(actor=ana, total=Decimal("12.40"), concepto="Cena", categoria_id=None, **comun)
    assert entorno.leer_gasto(nuevo_id)["revisado"] is True
