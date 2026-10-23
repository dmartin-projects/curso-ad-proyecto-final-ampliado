"""Ninguna puerta se salta el segundo factor (módulo 92).

Hay CUATRO sitios donde se abre una sesión: contraseña y proveedor, en la SPA y en el authorization server (módulos
90 y 91). Y dos caminos que dependen de una de ellas: el flujo OAuth (/authorize da codes a quien tenga la sesión del
authorization server) y el device flow (/device/ también). Con el MFA activo, ninguno da nada sin el segundo factor; y
completándolo, todos.
"""

from urllib.parse import parse_qs, urlencode, urlsplit

import jwt
import pytest
from django.test import Client

from conftest import UsuarioFactory
from oauth.tests.infrastructure.flujo import (
    canjear,
    con_sesion,
    consentir,
    peticion,
    pkce,
    refrescar,
    registrar,
    vuelta,
)
from usuarios.models import IdentidadExterna, Sesion
from usuarios.tests.infrastructure.api.v1.test_social_api import SPA, login_google
from usuarios.tests.infrastructure.ayudas_mfa import A, activar_mfa, codigo

pytestmark = pytest.mark.django_db
AUTORIZAR = "/api/oauth/authorize/"


@pytest.fixture
def ana(proveedores):
    """Con contraseña, con su Google vinculado y con el MFA activo."""
    ana = UsuarioFactory(email="ana@example.com")
    IdentidadExterna.objects.create(usuario=ana, proveedor="google", sub="sub-ana", email="ana@gmail.com")
    ana.secreto, ana.codigos = activar_mfa(ana)
    registrar()  # gastos-cli
    return ana


def siguiente() -> str:
    """Una petición de autorización del CLI (lo que lleva el `next` del login del authorization server)."""
    return AUTORIZAR + "?" + urlencode(peticion(pkce()[1]))


def destino(r) -> tuple[str, dict]:
    assert r.status_code == 302, r.content[:300]
    partes = urlsplit(r["Location"])
    return partes.path, {k: v[0] for k, v in parse_qs(partes.query).items()}


# ── Las cuatro puertas, con el primer factor y nada más ──


def spa_contrasena(navegador, ana, proveedores):
    r = navegador.post(
        A + "login/", {"email": ana.email, "password": "clave-segura-123"}, content_type="application/json"
    )
    assert r.status_code == 200 and "access" not in r.json() and "refresh" not in r.cookies
    return "spa", "contrasena"


def spa_proveedor(navegador, ana, proveedores):
    r = login_google(navegador, proveedores.google, sub="sub-ana")
    assert destino(r) == ("/login/segundo-factor", {"volver": "/"}) and "refresh" not in r.cookies
    return "spa", "proveedor"


def as_contrasena(navegador, ana, proveedores):
    r = navegador.post(
        "/api/oauth/login/?" + urlencode({"next": siguiente()}), {"username": ana.email, "password": "clave-segura-123"}
    )
    assert destino(r)[0] == "/api/oauth/segundo-factor/"
    return "autorizacion", "contrasena"


def as_proveedor(navegador, ana, proveedores):
    ida = navegador.get(f"{A}social/google/entrar/", {"para": "autorizar", "volver": siguiente()})["Location"]
    r = vuelta_social(navegador, proveedores, ida)
    assert r["Location"].startswith(f"{SPA}/api/oauth/segundo-factor/?next=")
    return "autorizacion", "proveedor"


def vuelta_social(navegador, proveedores, ida):
    from usuarios.tests.infrastructure.api.v1.test_social_api import vuelta as vuelta_del_proveedor

    return vuelta_del_proveedor(navegador, "google", proveedores.google.autorizar(ida, sub="sub-ana"))


PUERTAS = [spa_contrasena, spa_proveedor, as_contrasena, as_proveedor]


@pytest.mark.parametrize("puerta", PUERTAS, ids=lambda p: p.__name__)
def test_ninguna_puerta_abre_una_sesion_sin_el_segundo_factor(ana, proveedores, puerta):
    navegador = Client()
    puerta(navegador, ana, proveedores)
    assert not Sesion.objects.filter(usuario=ana).exists()  # ninguna sesión de Gastos…
    assert navegador.post(A + "refresh/").status_code == 401  # …ni refresh de la SPA…
    _, challenge = pkce()
    r = navegador.get(AUTORIZAR, peticion(challenge))  # …ni la del authorization server: /authorize no da codes…
    assert destino(r)[0] == "/api/oauth/login/"
    assert destino(navegador.get("/api/oauth/device/"))[0] == "/api/oauth/login/"  # …ni el device flow


@pytest.mark.parametrize("puerta", PUERTAS, ids=lambda p: p.__name__)
def test_con_el_segundo_factor_todas_abren_su_sesion(ana, proveedores, puerta):
    navegador = Client()
    canal, primero = puerta(navegador, ana, proveedores)
    if canal == "spa":
        r = navegador.post(
            A + "mfa/", {"factor": "totp", "codigo": codigo(ana.secreto)}, content_type="application/json"
        )
        assert r.status_code == 200 and r.cookies["refresh"]
    else:
        r = navegador.post("/api/oauth/segundo-factor/", {"codigo": codigo(ana.secreto), "next": siguiente()})
        assert destino(r)[0] == AUTORIZAR
        assert navegador.get(AUTORIZAR, peticion(pkce()[1])).status_code == 200  # el consentimiento
    sesion = Sesion.objects.get(usuario=ana)
    assert (sesion.canal, sorted(sesion.factores)) == (canal, sorted([primero, "totp"]))


def test_el_segundo_factor_del_authorization_server_con_un_codigo_de_recuperacion(ana):
    navegador = Client()
    as_contrasena(navegador, ana, None)
    pagina = navegador.get("/api/oauth/segundo-factor/", {"next": siguiente()})
    assert pagina.status_code == 200 and "código de recuperación" in pagina.content.decode()
    r = navegador.post("/api/oauth/segundo-factor/", {"factor": "totp", "codigo": "000000", "next": siguiente()})
    assert r.status_code == 400 and "El código no es correcto" in r.content.decode()
    datos = {"factor": "recuperacion", "codigo": ana.codigos[0], "next": siguiente()}
    assert destino(navegador.post("/api/oauth/segundo-factor/", datos))[0] == AUTORIZAR


def test_el_segundo_factor_del_authorization_server_solo_vuelve_a_si_mismo(ana):
    for i, fuera in enumerate(("https://otra.example/", "//otra.example/", "/api/v1/auth/me/")):
        navegador = Client()
        as_contrasena(navegador, ana, None)
        datos = {"factor": "recuperacion", "codigo": ana.codigos[i], "next": fuera}
        assert destino(navegador.post("/api/oauth/segundo-factor/", datos))[0] == "/api/oauth/login/"


# ── El ID token cuenta cómo se autenticó ──


def test_el_id_token_lleva_amr_acr_y_auth_time_de_la_autenticacion_real(ana):
    navegador = Client()
    as_contrasena(navegador, ana, None)
    navegador.post("/api/oauth/segundo-factor/", {"codigo": codigo(ana.secreto), "next": siguiente()})
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge, scope="openid gastos:leer")))["code"]
    tokens = canjear(code, verifier).json()
    claims = jwt.decode(tokens["id_token"], options={"verify_signature": False})
    momento = int(Sesion.objects.get(usuario=ana).autenticada.timestamp())
    assert (claims["amr"], claims["acr"], claims["auth_time"]) == (["mfa", "otp", "pwd"], "urn:gastos:acr:mfa", momento)
    # Un ID token renovado (con el refresh) cuenta la misma autenticación: la que dio el acceso
    renovado = jwt.decode(refrescar(tokens["refresh_token"]).json()["id_token"], options={"verify_signature": False})
    assert (renovado["amr"], renovado["auth_time"]) == (claims["amr"], claims["auth_time"])


def test_sin_mfa_el_id_token_dice_un_factor():
    luis = UsuarioFactory(email="luis@example.com")
    registrar()
    navegador = Client()
    navegador.post("/api/oauth/login/", {"username": luis.email, "password": "clave-segura-123"})
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge, scope="openid")))["code"]
    claims = jwt.decode(canjear(code, verifier).json()["id_token"], options={"verify_signature": False})
    assert (claims["amr"], claims["acr"]) == (["pwd"], "urn:gastos:acr:1fa")


def test_el_discovery_anuncia_amr_y_acr():
    datos = Client().get("/api/oauth/.well-known/openid-configuration").json()
    assert datos["acr_values_supported"] == ["urn:gastos:acr:1fa", "urn:gastos:acr:mfa"]
    assert {"amr", "acr", "auth_time"} <= set(datos["claims_supported"])


# ── La sesión del authorization server sigue a la de Gastos ──


def test_cerrar_la_sesion_del_authorization_server_desde_la_spa():
    luis = UsuarioFactory(email="luis@example.com")
    registrar()
    navegador = Client()
    navegador.post("/api/oauth/login/", {"username": luis.email, "password": "clave-segura-123"})
    assert navegador.get(AUTORIZAR, peticion(pkce()[1])).status_code == 200
    spa = Client()
    access = spa.post(
        A + "login/", {"email": luis.email, "password": "clave-segura-123"}, content_type="application/json"
    )
    cabecera = {"HTTP_AUTHORIZATION": f"Bearer {access.json()['access']}"}
    sesiones = spa.get(A + "sesiones/", **cabecera).json()
    assert {s["canal"] for s in sesiones} == {"spa", "autorizacion"}
    assert spa.post(A + "sesiones/cerrar-las-demas/", **cabecera).json() == {"cerradas": 1}
    assert destino(navegador.get(AUTORIZAR, peticion(pkce()[1])))[0] == "/api/oauth/login/"  # ya no da acceso


def test_una_sesion_de_django_sin_sesion_de_gastos_no_vale():
    """La de antes del módulo 92 (o una abierta sin pasar por IniciarSesionUseCase): fuera, al login."""
    luis = UsuarioFactory()
    registrar()
    navegador = Client()
    navegador.force_login(luis)
    assert destino(navegador.get(AUTORIZAR, peticion(pkce()[1])))[0] == "/api/oauth/login/"


def test_salir_del_authorization_server_cierra_su_sesion_de_gastos():
    """«¿No eres tú?» (o volver a entrar con prompt=login): la sesión de Gastos de ese navegador, cerrada también.
    Si no, seguiría «abierta» en «Sesiones» sin que nadie pudiera usarla."""
    luis = UsuarioFactory(email="luis@example.com")
    registrar()
    navegador = Client()
    navegador.post("/api/oauth/login/", {"username": luis.email, "password": "clave-segura-123"})
    assert Sesion.objects.filter(usuario=luis, cerrada__isnull=True).count() == 1
    assert navegador.post("/api/oauth/salir/").status_code == 302
    assert not Sesion.objects.filter(usuario=luis, cerrada__isnull=True).exists()
    navegador.post("/api/oauth/login/", {"username": luis.email, "password": "clave-segura-123"})
    navegador.get(AUTORIZAR, peticion(pkce()[1], prompt="login"))  # volver a entrar: la de antes, cerrada
    assert not Sesion.objects.filter(usuario=luis, cerrada__isnull=True).exists()


# ── acr_values: el cliente pide el multifactor (OIDC Core §3.1.2.1) ──


def test_con_acr_values_mfa_una_sesion_de_un_factor_vuelve_a_entrar(ana):
    """Una sesión abierta antes de activar el MFA es de un factor: con acr_values=urn:gastos:acr:mfa, otra vez al
    login (que ahora pide el segundo factor). Con la sesión de dos factores, la pantalla de consentimiento."""
    luis = UsuarioFactory(email="luis@example.com")
    navegador = con_sesion(luis)  # un factor
    activar_mfa(luis)
    mfa = {"acr_values": "urn:gastos:acr:mfa"}
    path, datos = destino(navegador.get(AUTORIZAR, peticion(pkce()[1], **mfa)))
    assert path == "/api/oauth/login/" and "acr_values=urn" in datos["next"]  # la petición sigue pidiéndolo
    assert not Sesion.objects.filter(usuario=luis, cerrada__isnull=True).exists()  # la de un factor, cerrada
    # Con dos factores, sí
    as_contrasena(navegador, ana, None)
    navegador.post("/api/oauth/segundo-factor/", {"codigo": codigo(ana.secreto), "next": siguiente()})
    assert navegador.get(AUTORIZAR, peticion(pkce()[1], **mfa)).status_code == 200


def test_con_acr_values_mfa_y_sin_segundo_factor_login_required():
    """Una cuenta sin TOTP no puede dar una sesión de dos factores en estas páginas: login_required, sin pantallas."""
    luis = UsuarioFactory(email="luis@example.com")
    registrar()
    navegador = con_sesion(luis)
    r = navegador.get(AUTORIZAR, peticion(pkce()[1], acr_values="urn:gastos:acr:mfa"))
    assert vuelta(r)["error"] == "login_required"
    assert navegador.get(AUTORIZAR, peticion(pkce()[1])).status_code == 200  # sin pedirlo, como siempre
