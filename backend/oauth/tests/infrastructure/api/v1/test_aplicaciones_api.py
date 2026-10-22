"""Aplicaciones conectadas en la API de la cuenta (ejercicio 1 del módulo 90)."""

import pytest
from oauth2_provider.models import RefreshToken
from rest_framework.test import APIClient

from conftest import UsuarioFactory
from oauth.tests.infrastructure.flujo import registrar, tokens

pytestmark = pytest.mark.django_db
URL = "/api/v1/auth/aplicaciones/"


@pytest.fixture
def ana(cliente):
    registrar(nombre="Gastos CLI")
    ana = UsuarioFactory()
    return ana, cliente(ana)


def test_lista_lo_que_has_dado_y_a_quien(ana):
    usuario, spa = ana
    tokens(usuario, scope="openid gastos:leer")
    tokens(usuario, scope="openid email gastos:leer gastos:escribir")  # otra sesión, con más scopes
    registrar("otra-app")
    tokens(UsuarioFactory(), client_id="otra-app")  # las de otro usuario no salen
    (app,) = spa.get(URL).json()
    assert (app["client_id"], app["nombre"]) == ("gastos-cli", "Gastos CLI")
    assert app["scopes"] == ["email", "gastos:escribir", "gastos:leer", "openid"]
    assert app["desde"] <= app["ultimo_uso"]


def test_retirar_el_acceso_corta_sus_tokens_al_momento(ana):
    usuario, spa = ana
    t = tokens(usuario)
    con_token = APIClient()
    con_token.credentials(HTTP_AUTHORIZATION=f"Bearer {t['access_token']}")
    assert con_token.get("/api/v1/hogares/").status_code == 200

    assert spa.delete(f"{URL}gastos-cli/").status_code == 204
    assert con_token.get("/api/v1/hogares/").status_code == 401  # el access token, también (no espera 10 min)
    assert spa.get(URL).json() == []
    assert spa.delete(f"{URL}gastos-cli/").status_code == 404


def test_un_access_token_sin_refresh_tambien_se_retira(ana):
    """Un access token vigente sin refresh (p. ej., su refresh revocado por el cliente) sigue dando acceso hasta que
    caduca: la aplicación sale en la lista y se le puede retirar."""
    usuario, spa = ana
    t = tokens(usuario)
    RefreshToken.objects.filter(user=usuario).delete()  # solo queda el access token
    con_token = APIClient()
    con_token.credentials(HTTP_AUTHORIZATION=f"Bearer {t['access_token']}")
    assert con_token.get("/api/v1/hogares/").status_code == 200
    assert [a["client_id"] for a in spa.get(URL).json()] == ["gastos-cli"]
    assert spa.delete(f"{URL}gastos-cli/").status_code == 204
    assert con_token.get("/api/v1/hogares/").status_code == 401


def test_una_aplicacion_no_ve_ni_toca_las_aplicaciones_conectadas(ana):
    usuario, _ = ana
    t = tokens(usuario, scope="openid gastos:leer gastos:escribir")
    con_token = APIClient()
    con_token.credentials(HTTP_AUTHORIZATION=f"Bearer {t['access_token']}")
    assert con_token.get(URL).status_code == 401
    assert con_token.delete(f"{URL}gastos-cli/").status_code == 401


def test_sin_sesion(ana):
    assert APIClient().get(URL).status_code == 401
