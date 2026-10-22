"""Ejercicio 1 del módulo 87, desde la API: la regla del borrado de cuentas, en su use case."""

import pytest

from conftest import CuentaFactory, MovimientoFactory
from finanzas.models import Cuenta

pytestmark = pytest.mark.django_db


def test_borrar_una_cuenta_con_movimientos_es_409(cliente, hogar_con_roles):
    hogar, roles = hogar_con_roles
    con, sin = CuentaFactory(hogar=hogar), CuentaFactory(hogar=hogar)
    MovimientoFactory(cuenta=con)
    c = cliente(roles["admin"])
    r = c.delete(f"/api/v1/hogares/{hogar.pk}/cuentas/{con.pk}/")
    assert r.status_code == 409 and r.json()["type"] == "cuenta_con_movimientos"
    assert c.delete(f"/api/v1/hogares/{hogar.pk}/cuentas/{sin.pk}/").status_code == 204
    assert list(Cuenta.objects.filter(hogar=hogar)) == [con]
