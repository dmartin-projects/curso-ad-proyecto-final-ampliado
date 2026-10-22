"""Device authorization grant, RFC 8628 (ejercicio 3 del módulo 90)."""

from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone
from oauth2_provider.models import DeviceGrant
from rest_framework.test import APIClient

from conftest import UsuarioFactory
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.tests.infrastructure.flujo import registrar

pytestmark = pytest.mark.django_db
DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"


@pytest.fixture
def tele():
    return registrar("gastos-tv", tipo=TipoCliente.DISPOSITIVO, scopes="gastos:leer", redirect_uris=())


def pedir_codigo(client_id="gastos-tv", scope="gastos:leer"):
    """Lo que hace el dispositivo: POST form-urlencoded (RFC 8628 §3.1)."""
    return Client().post(
        "/api/oauth/device-authorization/",
        f"client_id={client_id}&scope={scope.replace(' ', '+').replace(':', '%3A')}",
        content_type="application/x-www-form-urlencoded",
    )


def preguntar(device_code, client_id="gastos-tv"):
    datos = {"grant_type": DEVICE_CODE, "device_code": device_code, "client_id": client_id}
    return Client().post("/api/oauth/token/", datos)


def persona(usuario=None):
    navegador = Client()
    navegador.force_login(usuario or UsuarioFactory())
    return navegador


def escribir_y_decidir(navegador, user_code, accion="accept"):
    r = navegador.post("/api/oauth/device/", {"user_code": user_code})
    assert r.status_code == 302, r.content[:300]
    return navegador.post(r.headers["Location"], {"action": accion})


def test_el_flujo_entero(tele, time_machine):
    ana = UsuarioFactory()
    d = pedir_codigo().json()
    assert d["verification_uri"] == "http://localhost:8000/api/oauth/device/"
    assert d["verification_uri_complete"] == f"http://localhost:8000/api/oauth/device/?user_code={d['user_code']}"
    assert d["interval"] == 5 and len(d["user_code"]) == 8

    time_machine.move_to(timezone.now() + timedelta(seconds=5))
    assert preguntar(d["device_code"]).json()["error"] == "authorization_pending"

    # La persona, en su móvil: escribe el código como lo ve en la terminal (ABCD-EFGH, en minúsculas…) y acepta
    pantalla = persona(ana).get("/api/oauth/device/")
    assert "Nunca escribas un código que te haya dado otra persona" in pantalla.content.decode()
    navegador = persona(ana)
    r = navegador.post("/api/oauth/device/", {"user_code": f"{d['user_code'][:4]}-{d['user_code'][4:]}".lower()})
    confirmar = navegador.get(r.headers["Location"])
    assert "¿Conectar «gastos-tv» a tu cuenta?" in confirmar.content.decode()
    assert navegador.post(r.headers["Location"], {"action": "accept"}).status_code == 302

    time_machine.move_to(timezone.now() + timedelta(seconds=5))
    t = preguntar(d["device_code"]).json()
    assert t["access_token"].startswith("gst_at_") and t["scope"] == "gastos:leer" and "id_token" not in t
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {t['access_token']}")
    assert c.get("/api/v1/hogares/").status_code == 200  # en nombre de Ana

    # Un device_code da UN par de tokens (si alguien lo copia de la terminal después, no le sirve)
    time_machine.move_to(timezone.now() + timedelta(seconds=5))
    assert preguntar(d["device_code"]).json()["error"] == "expired_token"


def test_preguntar_demasiado_deprisa_es_slow_down(tele, time_machine):
    d = pedir_codigo().json()
    assert preguntar(d["device_code"]).json()["error"] == "slow_down"  # antes del primer intervalo
    time_machine.move_to(timezone.now() + timedelta(seconds=5))
    assert preguntar(d["device_code"]).json()["error"] == "authorization_pending"
    assert preguntar(d["device_code"]).json()["error"] == "slow_down"


def test_si_la_persona_cancela(tele, time_machine):
    d = pedir_codigo().json()
    escribir_y_decidir(persona(), d["user_code"], "deny")
    time_machine.move_to(timezone.now() + timedelta(seconds=5))
    assert preguntar(d["device_code"]).json()["error"] == "access_denied"


def test_el_codigo_caduca(tele, time_machine):
    d = pedir_codigo().json()
    time_machine.move_to(timezone.now() + timedelta(seconds=d["expires_in"] + 1))
    assert preguntar(d["device_code"]).json()["error"] == "expired_token"
    r = persona().post("/api/oauth/device/", {"user_code": d["user_code"]})
    assert r.status_code == 200 and "ha caducado o ya se ha usado" in r.content.decode()


def test_un_codigo_solo_se_usa_una_vez_y_solo_lo_confirma_quien_lo_escribio(tele):
    d = pedir_codigo().json()
    ana = persona()
    r = ana.post("/api/oauth/device/", {"user_code": d["user_code"]})
    assert persona().get(r.headers["Location"]).status_code == 404  # otra persona no puede confirmarlo
    ana.post(r.headers["Location"], {"action": "accept"})
    r = persona().post("/api/oauth/device/", {"user_code": d["user_code"]})
    assert r.status_code == 200 and "ya se ha usado" in r.content.decode()


def test_un_codigo_inventado(tele):
    r = persona().post("/api/oauth/device/", {"user_code": "AAAAAAAA"})
    assert r.status_code == 200 and "Ese código no existe" in r.content.decode()


def test_probar_codigos_tiene_limite(tele):
    navegador = persona()
    for _ in range(5):
        navegador.post("/api/oauth/device/", {"user_code": "AAAAAAAA"})
    assert navegador.post("/api/oauth/device/", {"user_code": "BBBBBBBB"}).status_code == 429


@pytest.mark.parametrize("scope", ["gastos:escribir", "operaciones:leer", "openid", ""])
def test_solo_los_scopes_del_cliente(tele, scope):
    r = pedir_codigo(scope=scope)
    assert r.status_code == 400 and r.json()["error"] == "invalid_scope"
    assert not DeviceGrant.objects.exists()  # sin código: la persona no llega a ver lo que no se concedería


def test_un_cliente_de_otro_tipo_no_usa_el_device_flow(tele):
    registrar()  # gastos-cli: authorization code
    r = pedir_codigo(client_id="gastos-cli", scope="gastos:leer")
    assert r.status_code in (400, 401) and not DeviceGrant.objects.exists()


def test_discovery_anuncia_el_endpoint():
    meta = Client().get("/api/oauth/.well-known/openid-configuration").json()
    assert meta["device_authorization_endpoint"] == "http://localhost:8000/api/oauth/device-authorization/"
