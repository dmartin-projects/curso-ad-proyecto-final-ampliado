"""La API de Gastos como resource server (módulo 90): scopes Y rol en el hogar, y lo que un token OAuth no abre."""

import base64
from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient

from conftest import CuentaFactory, MovimientoFactory
from finanzas.models import Movimiento
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.tests.infrastructure.flujo import registrar, tokens

pytestmark = pytest.mark.django_db
TODO = "openid gastos:leer gastos:escribir"


@pytest.fixture
def escenario(hogar_con_roles):
    registrar()
    hogar, roles = hogar_con_roles
    return hogar, roles, CuentaFactory(hogar=hogar, nombre="Común")


def con_token(access_token) -> APIClient:
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return c


def url(hogar, recurso="movimientos"):
    return f"/api/v1/hogares/{hogar.pk}/{recurso}/"


def gasto(cuenta):
    return {"fecha": "2026-10-01", "importe": "-12.50", "concepto": "Pan", "cuenta": cuenta.pk}


# ── La intersección: lo que permite el scope Y lo que permite el rol ──
@pytest.mark.parametrize(
    "rol, scope, esperado, motivo",
    [
        ("miembro", TODO, 201, None),
        ("admin", TODO, 201, None),
        ("admin", "openid gastos:leer", 403, "insufficient_scope"),  # el rol da, el scope no
        ("lector", TODO, 403, "sin_permiso"),  # el scope da, el rol no
        ("ajeno", TODO, 404, None),  # ni siquiera sabe que el hogar existe (como siempre)
    ],
)
def test_crear_un_movimiento_exige_scope_y_rol(escenario, rol, scope, esperado, motivo):
    hogar, roles, cuenta = escenario
    t = tokens(roles[rol], scope=scope)
    r = con_token(t["access_token"]).post(url(hogar), gasto(cuenta))
    assert r.status_code == esperado, r.json()
    if motivo == "insufficient_scope":
        assert (
            r.headers["WWW-Authenticate"] == 'Bearer realm="api", error="insufficient_scope", scope="gastos:escribir"'
        )
    elif motivo:
        assert r.json()["type"] == motivo


def test_lo_creado_con_un_token_queda_a_nombre_del_usuario(escenario):
    hogar, roles, cuenta = escenario
    t = tokens(roles["miembro"], scope=TODO)
    r = con_token(t["access_token"]).post(url(hogar), gasto(cuenta))
    assert Movimiento.objects.get(pk=r.json()["id"]).creado_por == roles["miembro"]


@pytest.mark.parametrize("ruta", ["", "movimientos", "cuentas", "categorias", "dashboard"], ids=lambda r: r or "hogar")
def test_con_gastos_leer_se_lee(escenario, ruta):
    hogar, roles, _ = escenario
    c = con_token(tokens(roles["lector"], scope="openid gastos:leer")["access_token"])
    r = c.get(f"/api/v1/hogares/{hogar.pk}/{ruta}/".replace("//", "/"))
    assert r.status_code == 200, r.json()


def test_sin_gastos_leer_no_se_lee(escenario):
    hogar, roles, _ = escenario
    c = con_token(tokens(roles["admin"], scope="openid email")["access_token"])
    for ruta in ("/api/v1/hogares/", url(hogar), url(hogar, "dashboard")):
        r = c.get(ruta)
        assert (
            r.status_code == 403 and 'error="insufficient_scope", scope="gastos:leer"' in r.headers["WWW-Authenticate"]
        )


def test_lo_que_no_se_delega_no_se_hace_con_ningun_scope(escenario):
    """Editar, borrar o recategorizar movimientos, crear categorías, gestionar el hogar: solo desde la app."""
    hogar, roles, cuenta = escenario
    m = MovimientoFactory(cuenta=cuenta)
    c = con_token(tokens(roles["admin"], scope=TODO)["access_token"])
    respuestas = [
        c.delete(f"{url(hogar)}{m.pk}/"),
        c.patch(f"{url(hogar)}{m.pk}/", {"concepto": "Otro"}),
        c.post(url(hogar, "categorias"), {"nombre": "Nueva"}),
        c.patch(f"/api/v1/hogares/{hogar.pk}/", {"nombre": "Mío"}),
        c.delete(f"/api/v1/hogares/{hogar.pk}/"),
        c.post(f"/api/v1/hogares/{hogar.pk}/miembros/invitar/", {"email": "x@example.com", "rol": "admin"}),
    ]
    assert [r.status_code for r in respuestas] == [403, 403, 403, 403, 403, 401]
    assert Movimiento.objects.filter(pk=m.pk).exists()


# ── Lo que un token OAuth no abre: la cuenta, la autenticación, el backoffice ──
@pytest.mark.parametrize(
    "metodo, ruta",
    [
        ("get", "/api/v1/auth/me/"),
        ("post", "/api/v1/auth/cambiar-password/"),
        ("post", "/api/v1/auth/refresh/"),
        ("get", "/api/v1/notificaciones/"),
        ("get", "/api/v1/backoffice/resumen/"),
        ("get", "/api/v1/backoffice/usuarios/"),
    ],
)
def test_un_token_oauth_no_sirve_para_la_cuenta_ni_el_backoffice(escenario, metodo, ruta):
    _, roles, _ = escenario
    roles["admin"].is_staff = True
    roles["admin"].save(update_fields=["is_staff"])
    c = con_token(tokens(roles["admin"], scope=TODO)["access_token"])
    r = getattr(c, metodo)(ruta)
    assert r.status_code == 401  # para estas views es un Bearer que no entienden


# ── Tokens que no valen ──
def test_token_inventado_caducado_o_revocado(escenario, time_machine):
    hogar, roles, _ = escenario
    t = tokens(roles["lector"])
    r = con_token("gst_at_inventado").get(url(hogar))
    assert r.status_code == 401 and r.headers["WWW-Authenticate"] == 'Bearer realm="api", error="invalid_token"'

    Client().post("/api/oauth/revoke_token/", {"token": t["access_token"], "client_id": "gastos-cli"})
    assert con_token(t["access_token"]).get(url(hogar)).status_code == 401

    t = tokens(roles["lector"])
    time_machine.move_to(timezone.now() + timedelta(seconds=601))
    assert con_token(t["access_token"]).get(url(hogar)).status_code == 401


def test_el_token_de_un_usuario_desactivado_no_vale(escenario):
    hogar, roles, _ = escenario
    t = tokens(roles["lector"])
    roles["lector"].is_active = False
    roles["lector"].save(update_fields=["is_active"])
    assert con_token(t["access_token"]).get(url(hogar)).status_code == 401


def test_el_token_en_la_url_no_vale(escenario):
    """RFC 9700 §4.3.2 / RFC 6750 §2.3: en la URL acaba en logs, historiales y Referer. Solo en la cabecera."""
    hogar, roles, _ = escenario
    t = tokens(roles["lector"])
    r = APIClient().get(url(hogar), {"access_token": t["access_token"]})
    assert r.status_code == 401


def test_la_spa_sigue_igual(escenario):
    """El JWT de la SPA no tiene scopes: su usuario puede todo lo que le deja su rol, como siempre."""
    hogar, roles, cuenta = escenario
    login = APIClient().post("/api/v1/auth/login/", {"email": roles["admin"].email, "password": "clave-segura-123"})
    c = con_token(login.json()["access"])
    assert c.post(url(hogar), gasto(cuenta)).status_code == 201
    assert c.patch(f"/api/v1/hogares/{hogar.pk}/", {"nombre": "Mío"}).status_code == 200


# ── Un servicio (client credentials) ──
def token_de_servicio(scope="operaciones:leer"):
    monitor = registrar("monitor", tipo=TipoCliente.SERVICIO, scopes="operaciones:leer", redirect_uris=())
    basic = base64.b64encode(f"monitor:{monitor.client_secret}".encode()).decode()
    r = Client().post(
        "/api/oauth/token/", {"grant_type": "client_credentials", "scope": scope}, HTTP_AUTHORIZATION=f"Basic {basic}"
    )
    return r.json()["access_token"]


def test_un_servicio_lee_el_estado(escenario):
    r = con_token(token_de_servicio()).get("/api/v1/backoffice/estado/")
    assert r.status_code == 200 and "tickets_atascados" in r.json()


def test_el_estado_solo_para_servicios(escenario):
    _, roles, _ = escenario
    roles["admin"].is_staff = True
    roles["admin"].save(update_fields=["is_staff"])
    jwt_spa = APIClient().post("/api/v1/auth/login/", {"email": roles["admin"].email, "password": "clave-segura-123"})
    assert con_token(jwt_spa.json()["access"]).get("/api/v1/backoffice/estado/").status_code == 401  # ni el personal
    assert APIClient().get("/api/v1/backoffice/estado/").status_code == 401
    usuario = con_token(tokens(roles["admin"], scope=TODO)["access_token"])
    assert usuario.get("/api/v1/backoffice/estado/").status_code == 403  # un token de usuario, no de servicio


def test_un_token_de_servicio_no_actua_como_usuario(escenario):
    hogar, *_ = escenario
    c = con_token(token_de_servicio())
    assert c.get("/api/v1/hogares/").status_code == 403
    assert c.get(url(hogar)).status_code == 403


def test_openapi_documenta_el_scope_de_cada_operacion(escenario):
    esquema = APIClient().get("/api/schema/?format=json").json()
    oauth2 = esquema["components"]["securitySchemes"]["oauth2"]
    assert oauth2["flows"]["authorizationCode"]["authorizationUrl"] == "/api/oauth/authorize/"
    movimientos = esquema["paths"]["/api/v1/hogares/{hogar_pk}/movimientos/"]
    assert {"oauth2": ["gastos:escribir"]} in movimientos["post"]["security"]
    assert {"oauth2": ["gastos:leer"]} in movimientos["get"]["security"]
    detalle = esquema["paths"]["/api/v1/hogares/{hogar_pk}/movimientos/{id}/"]
    assert not any("oauth2" in s for s in detalle["delete"]["security"])  # borrar no se delega
