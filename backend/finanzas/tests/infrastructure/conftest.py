"""Los datos de un mes de un hogar, para el dashboard (módulos 77 y 87)."""

from datetime import date
from decimal import Decimal

import pytest

from conftest import CategoriaFactory, CuentaFactory, MovimientoFactory, PresupuestoFactory
from finanzas.models import Comercio

OCT = date(2026, 10, 1)


@pytest.fixture
def datos(hogar_con_roles):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    comida = CategoriaFactory(hogar=hogar, nombre="Comida", color="#4caf50")
    fruta = CategoriaFactory(hogar=hogar, nombre="Fruta", padre=comida)
    ocio = CategoriaFactory(hogar=hogar, nombre="Ocio")
    mercadona = Comercio.objects.create(nombre="Mercadona")

    def mov(dia, importe, categoria=None, mes=10, **extra):
        return MovimientoFactory(
            cuenta=cuenta, fecha=date(2026, mes, dia), importe=Decimal(importe), categoria=categoria, **extra
        )

    mov(1, "-10", comida, comercio=mercadona)
    mov(1, "-5", fruta, comercio=mercadona)
    mov(3, "-20", ocio)
    mov(3, "1000.00")
    mov(7, "-2.50", comida, revisado=False)
    mov(5, "-30", ocio, mes=9)
    PresupuestoFactory(hogar=hogar, categoria=comida, mes=OCT, importe=Decimal("10"))
    return hogar, roles, comida, ocio
