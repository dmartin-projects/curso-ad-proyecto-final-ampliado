"""Módulo 90: un token OAuth en la API de finanzas. El resto de casos, en oauth/tests/infrastructure/api/test_api.py."""

import pytest
from rest_framework.test import APIClient

from conftest import CuentaFactory, MovimientoFactory
from finanzas.infrastructure.api.v1.views.movimiento_viewset import MovimientoViewSet
from finanzas.models import Movimiento
from oauth.tests.infrastructure.flujo import registrar, tokens

pytestmark = pytest.mark.django_db


@pytest.fixture
def escenario(hogar_con_roles):
    registrar()
    hogar, roles = hogar_con_roles
    return hogar, roles, CuentaFactory(hogar=hogar, nombre="Común")


def url(hogar):
    return f"/api/v1/hogares/{hogar.pk}/movimientos/"


def con_token(access_token) -> APIClient:
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return c


def test_ningun_scope_da_poderes_de_administrador(escenario, monkeypatch):
    """Defensa en profundidad: si alguien añadiera el borrado a los scopes de la view, el Actor limitado por los
    scopes (gastos:escribir → MIEMBRO) seguiría sin poder borrar, que exige ADMIN (en RolEnHogar y en el use case)."""
    hogar, roles, cuenta = escenario
    m = MovimientoFactory(cuenta=cuenta)
    monkeypatch.setattr(MovimientoViewSet, "scopes_por_accion", {"destroy": "gastos:escribir"})
    r = con_token(tokens(roles["admin"], scope="openid gastos:leer gastos:escribir")["access_token"]).delete(
        f"{url(hogar)}{m.pk}/"
    )
    assert r.status_code == 403 and r.json()["type"] == "sin_permiso"
    assert Movimiento.objects.filter(pk=m.pk).exists()
