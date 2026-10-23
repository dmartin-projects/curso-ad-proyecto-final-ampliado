"""El authorization server (módulo 90): el flujo, y cada defensa con su test negativo."""

import base64
import hashlib
import json
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from django.contrib.auth.hashers import check_password
from django.test import Client
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken

from conftest import UsuarioFactory
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.models import ClienteOAuth
from oauth.tests.infrastructure.flujo import (
    canjear,
    con_sesion,
    consentir,
    peticion,
    pkce,
    refrescar,
    registrar,
    tokens,
    vuelta,
)

pytestmark = pytest.mark.django_db
EMISOR = "http://localhost:8000/api/oauth"


@pytest.fixture
def cli():
    return registrar()


@pytest.fixture
def ana():
    return UsuarioFactory(email="ana@example.com", nombre="Ana", apellidos="García")


@pytest.fixture
def navegador(ana):
    return con_sesion(ana)


def jwks():
    return Client().get("/api/oauth/.well-known/jwks.json").json()


def verificar(id_token, audience="gastos-cli"):
    """Lo que hace un cliente: la firma con la clave del JWKS de su kid, y los claims (como cli/gastos_cli.py)."""
    kid = jwt.get_unverified_header(id_token)["kid"]
    clave = next(k for k in jwks()["keys"] if k["kid"] == kid)
    return jwt.decode(id_token, jwt.PyJWK(clave).key, algorithms=["RS256"], audience=audience, issuer=EMISOR)


# ── El flujo entero ──
def test_authorization_code_con_pkce_de_principio_a_fin(cli, ana):
    navegador = Client()
    verifier, challenge = pkce()
    params = peticion(challenge, scope="openid email profile gastos:leer")

    # 1. Sin sesión en el authorization server: al login, que vuelve aquí después
    r = navegador.get("/api/oauth/authorize/", params)
    assert r.status_code == 302 and r.headers["Location"].startswith("/api/oauth/login/?next=/api/oauth/authorize/")
    r = navegador.post(r.headers["Location"], {"username": "ana@example.com", "password": "clave-segura-123"})
    assert r.status_code == 302 and r.headers["Location"].startswith("/api/oauth/authorize/?")

    # 2. La pantalla de consentimiento y "Permitir": vuelta a la redirect URI con el code, el state y el iss
    params_vuelta = vuelta(consentir(navegador, params))
    assert params_vuelta["state"] == "estado-123"
    assert params_vuelta["iss"] == EMISOR  # RFC 9207

    # 3. El code + el verifier → los tokens
    r = canjear(params_vuelta["code"], verifier)
    assert r.status_code == 200
    t = r.json()
    assert t["token_type"] == "Bearer" and t["expires_in"] == 600
    assert t["access_token"].startswith("gst_at_") and t["refresh_token"].startswith("gst_rt_")
    assert set(t["scope"].split()) == {"openid", "email", "profile", "gastos:leer"}

    # 4. El ID token: firmado con la clave del JWKS y con los claims de esta petición
    claims = verificar(t["id_token"])
    assert claims["sub"] == str(ana.pk) and claims["aud"] == "gastos-cli" and claims["iss"] == EMISOR
    assert claims["nonce"] == "nonce-456"
    assert claims["exp"] - claims["iat"] == 600 and claims["auth_time"] <= claims["iat"]
    assert claims["email"] == "ana@example.com" and claims["email_verified"] is True
    assert claims["name"] == "Ana García" and claims["locale"] == "es"
    # at_hash (OIDC Core §3.1.3.6): la mitad izquierda del SHA-256 del access token, que queda atado al ID token
    mitad = hashlib.sha256(t["access_token"].encode()).digest()[:16]
    assert claims["at_hash"] == base64.urlsafe_b64encode(mitad).rstrip(b"=").decode()

    # 5. /userinfo con el access token: los mismos claims (los de sus scopes)
    info = Client().get("/api/oauth/userinfo/", HTTP_AUTHORIZATION=f"Bearer {t['access_token']}").json()
    assert info["sub"] == str(ana.pk) and info["email"] == "ana@example.com" and info["given_name"] == "Ana"


def test_los_claims_salen_solo_con_su_scope(cli, ana):
    claims = verificar(tokens(ana, scope="openid gastos:leer")["id_token"])
    assert "email" not in claims and "name" not in claims  # sin email ni profile, solo el sub


def test_en_la_base_de_datos_solo_el_hash_de_cada_token(cli, ana):
    t = tokens(ana)
    acceso = AccessToken.objects.get()
    assert acceso.token == "" and acceso.token_checksum != t["access_token"]  # RFC 9700 §4: robar la BD no basta
    assert RefreshToken.objects.get().token == ""


# ── Discovery y JWKS ──
def test_discovery(cli):
    meta = Client().get("/api/oauth/.well-known/openid-configuration").json()
    assert meta["issuer"] == EMISOR
    assert meta["authorization_endpoint"] == f"{EMISOR}/authorize/"
    assert meta["token_endpoint"] == f"{EMISOR}/token/"
    assert meta["jwks_uri"] == f"{EMISOR}/.well-known/jwks.json"
    assert meta["revocation_endpoint"] == f"{EMISOR}/revoke_token/"
    assert meta["response_types_supported"] == ["code"]  # ni implicit ni hybrid
    assert meta["code_challenge_methods_supported"] == ["S256"]  # ni "plain"
    assert meta["id_token_signing_alg_values_supported"] == ["RS256"]
    assert meta["authorization_response_iss_parameter_supported"] is True
    assert {"email", "email_verified", "name"} <= set(meta["claims_supported"])


def test_el_jwks_publica_la_clave_publica_y_nada_mas(cli, ana):
    (clave,) = jwks()["keys"]
    assert clave["kty"] == "RSA" and clave["alg"] == "RS256" and clave["use"] == "sig"
    assert not {"d", "p", "q", "dp", "dq", "qi"} & set(clave)  # ninguna parte de la clave privada
    cabecera = jwt.get_unverified_header(tokens(ana)["id_token"])
    assert cabecera["kid"] == clave["kid"] and cabecera["alg"] == "RS256"


# ── PKCE ──
def test_sin_code_challenge_no_hay_code(cli, navegador):
    r = navegador.get("/api/oauth/authorize/", peticion(None, code_challenge_method=None))
    assert vuelta(r)["error"] == "invalid_request"  # con la redirect URI ya validada, el error vuelve al cliente


def test_pkce_plain_no_se_acepta(cli, navegador):
    verifier, _ = pkce()
    r = consentir(navegador, peticion(verifier, code_challenge_method="plain"))
    assert vuelta(r)["error"] == "invalid_request"


@pytest.mark.parametrize("verifier", ["otro-verifier-" + "x" * 40, None], ids=["incorrecto", "ausente"])
def test_el_code_sin_su_verifier_no_vale(cli, navegador, verifier):
    """Quien intercepta el code (otra app que escucha en el mismo puerto, un log, un Referer) no tiene el verifier."""
    _, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge)))["code"]
    r = canjear(code, verifier)
    assert r.status_code == 400 and r.json()["error"] in ("invalid_grant", "invalid_request")
    assert not AccessToken.objects.exists()


# ── El code ──
def test_un_code_solo_se_canjea_una_vez(cli, navegador):
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge)))["code"]
    assert canjear(code, verifier).status_code == 200
    r = canjear(code, verifier)
    assert r.status_code == 400 and r.json()["error"] == "invalid_grant"


def test_el_code_caduca_en_60_segundos(cli, navegador, time_machine):
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge)))["code"]
    time_machine.move_to(timezone.now() + timedelta(seconds=61))
    assert canjear(code, verifier).json()["error"] == "invalid_grant"


def test_el_code_de_un_cliente_no_lo_canjea_otro(cli, navegador):
    registrar("otra-app", redirect_uris=("https://otra.example.com/callback",))
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge)))["code"]
    r = canjear(code, verifier, redirect_uri="https://otra.example.com/callback", client_id="otra-app")
    assert r.status_code == 400 and r.json()["error"] == "invalid_grant"


def test_el_canje_lleva_la_misma_redirect_uri_que_la_peticion(cli, navegador):
    """Sin esto, un atacante podría inyectar en su sesión un code robado que se emitió para otra redirect URI."""
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge)))["code"]
    r = canjear(code, verifier, redirect_uri="http://127.0.0.1:9999/otra")
    assert r.status_code == 400 and r.json()["error"] in ("invalid_request", "invalid_grant")


# ── Redirect URI: exacta (salvo el puerto de loopback, RFC 8252) ──
@pytest.mark.parametrize(
    "redirect_uri",
    [
        "http://127.0.0.1:53682/otra-ruta",
        "http://127.0.0.1:53682/callback?extra=1",  # parámetros que no estaban registrados
        "http://localhost:53682/callback",  # localhost no es 127.0.0.1
        "https://127.0.0.1/callback",
        "https://atacante.example.com/callback",  # open redirect: el code iría a otro sitio
        "http://127.0.0.1.atacante.example.com/callback",
    ],
)
def test_una_redirect_uri_no_registrada_no_recibe_nada(cli, navegador, redirect_uri):
    _, challenge = pkce()
    r = navegador.get("/api/oauth/authorize/", peticion(challenge, redirect_uri=redirect_uri))
    # NO redirige (sería mandar el error, o el code, a quien no es): una página de error en el propio servidor
    assert r.status_code == 400 and "Location" not in r.headers
    assert b"Esta petici\xc3\xb3n no es v\xc3\xa1lida" in r.content


def test_el_puerto_de_loopback_puede_cambiar(cli, navegador):
    _, challenge = pkce()
    for puerto in (1024, 53682, 65000):
        r = consentir(navegador, peticion(challenge, redirect_uri=f"http://127.0.0.1:{puerto}/callback"))
        assert r.headers["Location"].startswith(f"http://127.0.0.1:{puerto}/callback?code=")


def test_un_cliente_desconocido_no_redirige(navegador):
    _, challenge = pkce()
    r = navegador.get("/api/oauth/authorize/", peticion(challenge, client_id="no-existe"))
    assert r.status_code == 400 and "Location" not in r.headers


# ── Scopes y consentimiento ──
def test_un_scope_que_el_cliente_no_tiene_no_se_concede(cli, navegador):
    _, challenge = pkce()
    r = navegador.get("/api/oauth/authorize/", peticion(challenge, scope="openid operaciones:leer"))
    assert vuelta(r)["error"] == "invalid_scope"


def test_sin_scope_no_hay_token(cli, navegador):
    _, challenge = pkce()
    r = navegador.get("/api/oauth/authorize/", peticion(challenge, scope=None))
    assert vuelta(r)["error"] == "invalid_scope"


def test_cambiar_el_scope_en_el_formulario_no_sirve(cli, navegador):
    """Los datos de la petición viajan en campos ocultos del formulario: el POST se vuelve a validar entero."""
    _, challenge = pkce()
    r = consentir(navegador, peticion(challenge), scope="openid operaciones:leer")
    assert vuelta(r)["error"] == "invalid_scope"
    assert not AccessToken.objects.exists()


def test_cancelar_devuelve_access_denied(cli, navegador):
    _, challenge = pkce()
    r = consentir(navegador, peticion(challenge), permitir=False)
    assert vuelta(r) == {"error": "access_denied", "state": "estado-123", "iss": EMISOR}


def test_la_pantalla_de_consentimiento(cli, navegador):
    _, challenge = pkce()
    r = navegador.get("/api/oauth/authorize/", peticion(challenge))
    html = r.content.decode()
    assert "«gastos-cli» quiere acceder a tu cuenta" in html and "ana@example.com" in html
    assert "Ver los movimientos, las cuentas y el resumen de tus hogares" in html
    assert r.headers["X-Frame-Options"] == "DENY"  # no se puede meter en un iframe (clickjacking)


def test_el_consentimiento_exige_el_token_csrf(cli, ana):
    """Sin CSRF, una página cualquiera podría enviar "Permitir" en nombre de un usuario con la sesión abierta."""
    navegador = con_sesion(ana, Client(enforce_csrf_checks=True))
    _, challenge = pkce()
    datos = navegador.get("/api/oauth/authorize/", peticion(challenge)).context["form"].initial
    r = navegador.post("/api/oauth/authorize/", {k: v for k, v in datos.items() if v is not None} | {"allow": "on"})
    assert r.status_code == 403


# ── Volver a autenticar: prompt=login y max_age (OIDC Core §3.1.2.1) ──
def al_login(respuesta) -> dict:
    """Adónde vuelve el login: los parámetros de la petición de autorización que lleva en `next`."""
    assert respuesta.status_code == 302 and respuesta["Location"].startswith("/api/oauth/login/?next="), respuesta
    siguiente = parse_qs(urlsplit(respuesta["Location"]).query)["next"][0]
    assert siguiente.startswith("/api/oauth/authorize/?")
    return {k: v[0] for k, v in parse_qs(urlsplit(siguiente).query).items()}


def test_max_age_vencido_vuelve_a_pedir_la_contrasena(cli, ana, time_machine):
    navegador = Client()
    navegador.post("/api/oauth/login/", {"username": "ana@example.com", "password": "clave-segura-123"})
    time_machine.move_to(timezone.now() + timedelta(hours=3))
    verifier, challenge = pkce()
    vuelve = al_login(navegador.get("/api/oauth/authorize/", peticion(challenge, max_age="3600")))
    assert "max_age" not in vuelve and vuelve["state"] == "estado-123"  # la misma petición; max_age, ya cumplido
    assert "_auth_user_id" not in navegador.session  # la sesión vieja, cerrada: el login no la reutiliza
    navegador.post("/api/oauth/login/", {"username": "ana@example.com", "password": "clave-segura-123"})
    code = vuelta(consentir(navegador, vuelve))["code"]
    claims = verificar(canjear(code, verifier).json()["id_token"])
    assert timezone.now().timestamp() - claims["auth_time"] < 60  # el auth_time es el del login de ahora


def test_max_age_dentro_de_plazo_no_pide_nada(cli, navegador):
    _, challenge = pkce()
    assert navegador.get("/api/oauth/authorize/", peticion(challenge, max_age="3600")).status_code == 200


def test_prompt_login_vuelve_a_pedir_la_contrasena_aunque_haya_sesion(cli, navegador):
    _, challenge = pkce()
    vuelve = al_login(navegador.get("/api/oauth/authorize/", peticion(challenge, prompt="login")))
    assert "prompt" not in vuelve
    assert navegador.get("/api/oauth/login/").status_code == 200  # la pantalla del login, no la vuelta directa


def test_prompt_none_sin_pantallas(cli, ana, navegador, time_machine):
    """prompt=none: el cliente no quiere pantallas. Sin sesión (o con una demasiado antigua), login_required; con
    sesión, consent_required: Gastos pregunta siempre."""
    _, challenge = pkce()
    sin_sesion = Client().get("/api/oauth/authorize/", peticion(challenge, prompt="none"))
    assert vuelta(sin_sesion) == {"error": "login_required", "state": "estado-123", "iss": EMISOR}
    con_sesion = navegador.get("/api/oauth/authorize/", peticion(challenge, prompt="none"))
    assert vuelta(con_sesion)["error"] == "consent_required"
    time_machine.move_to(timezone.now() + timedelta(hours=3))
    antigua = navegador.get("/api/oauth/authorize/", peticion(challenge, prompt="none", max_age="60"))
    assert vuelta(antigua)["error"] == "login_required"
    otra_uri = navegador.get(
        "/api/oauth/authorize/", peticion(challenge, prompt="none", redirect_uri="https://malo.example/")
    )
    assert otra_uri.status_code == 400  # a una redirect URI que no es del cliente, nada: ni el error


def test_un_max_age_que_no_es_un_numero_es_invalid_request(cli, navegador):
    _, challenge = pkce()
    assert (
        vuelta(navegador.get("/api/oauth/authorize/", peticion(challenge, max_age="-1")))["error"] == "invalid_request"
    )


def test_approval_prompt_de_la_url_no_se_salta_el_consentimiento(cli, ana, navegador):
    """DOT haría caso de ?approval_prompt=auto (sin pantalla si ya hay un token vivo con esos scopes): quien manda
    la URL no decide si se pregunta."""
    tokens(ana)  # ya le dio acceso una vez: hay un access token vivo
    _, challenge = pkce()
    r = navegador.get("/api/oauth/authorize/", peticion(challenge, approval_prompt="auto"))
    assert r.status_code == 200 and "quiere acceder a tu cuenta" in r.content.decode()


# ── El login del authorization server ──
def test_login_incorrecto(cli, ana):
    r = Client().post("/api/oauth/login/", {"username": "ana@example.com", "password": "mala"})
    assert r.status_code == 200 and "Email o contraseña incorrectos." in r.content.decode()


def test_login_con_limite_de_intentos(cli, ana):
    navegador = Client()
    for _ in range(5):
        navegador.post("/api/oauth/login/", {"username": "ana@example.com", "password": "mala"})
    r = navegador.post("/api/oauth/login/", {"username": "ana@example.com", "password": "clave-segura-123"})
    assert r.status_code == 429  # ni con la buena: 5 por minuto (el mismo límite que el login de la API)


def test_la_sesion_del_authorization_server_no_llega_a_la_api(cli, ana):
    navegador = Client()
    navegador.post("/api/oauth/login/", {"username": "ana@example.com", "password": "clave-segura-123"})
    galleta = navegador.cookies["sessionid"]
    assert galleta["path"] == "/api/oauth/" and galleta["httponly"]
    assert galleta["samesite"] == "Lax"  # la vuelta desde otra app es una navegación: Strict la perdería


# ── Grants que no existen aquí ──
def test_implicit_no(cli, navegador):
    _, challenge = pkce()
    for response_type in ("token", "id_token", "id_token token", "code id_token"):
        r = navegador.get("/api/oauth/authorize/", peticion(challenge, response_type=response_type))
        assert "access_token" not in r.headers.get("Location", "")
        assert r.status_code in (302, 400) and ("error=" in r.headers.get("Location", "") or r.status_code == 400)


def test_password_no_aunque_exista_una_aplicacion_de_ese_tipo(ana):
    """El dominio no deja registrar clientes "password"; aunque alguien cree uno con el ORM (con sus scopes), el
    servidor lo rechaza: el password grant da la contraseña del usuario a la aplicación (OAuth 2.1 lo elimina)."""
    vieja = Application.objects.create(
        client_id="vieja", client_type="confidential", authorization_grant_type="password",
        client_secret="secreto", name="Vieja",
    )  # fmt: skip
    ClienteOAuth.objects.create(aplicacion=vieja, tipo="web", scopes=["gastos:leer"])
    r = Client().post(
        "/api/oauth/token/",
        {
            "grant_type": "password",
            "username": "ana@example.com",
            "password": "clave-segura-123",
            "scope": "gastos:leer",
        },
        HTTP_AUTHORIZATION="Basic " + base64.b64encode(b"vieja:secreto").decode(),
    )
    assert r.status_code == 400 and "access_token" not in r.json()


# ── Refresh token: rotación y detección de reutilización ──
def test_el_refresh_token_rota(cli, ana):
    t1 = tokens(ana)
    r = refrescar(t1["refresh_token"])
    assert r.status_code == 200
    t2 = r.json()
    assert t2["refresh_token"] != t1["refresh_token"] and t2["access_token"] != t1["access_token"]
    assert refrescar(t2["refresh_token"]).status_code == 200


def test_un_refresh_token_reutilizado_revoca_toda_su_familia(cli, ana):
    """El viejo solo lo puede tener alguien que lo ha copiado: se corta la sesión entera (la del ladrón y la buena)."""
    t1 = tokens(ana)
    t2 = refrescar(t1["refresh_token"]).json()
    assert refrescar(t1["refresh_token"]).json()["error"] == "invalid_grant"  # el viejo, otra vez
    assert refrescar(t2["refresh_token"]).json()["error"] == "invalid_grant"  # y el nuevo ya tampoco vale
    r = Client().get("/api/oauth/userinfo/", HTTP_AUTHORIZATION=f"Bearer {t2['access_token']}")
    assert r.status_code == 401  # ni su access token


def test_una_cuenta_desactivada_no_renueva(cli, ana):
    t = tokens(ana)
    ana.is_active = False
    ana.save(update_fields=["is_active"])
    assert refrescar(t["refresh_token"]).json()["error"] == "invalid_grant"


def test_el_refresh_token_de_un_cliente_no_lo_usa_otro(cli, ana):
    registrar("otra-app", redirect_uris=("https://otra.example.com/callback",))
    t = tokens(ana)
    assert refrescar(t["refresh_token"], client_id="otra-app").json()["error"] == "invalid_grant"


# ── Revocación (RFC 7009) ──
def test_revocar_el_refresh_token_corta_la_sesion(cli, ana):
    t = tokens(ana)
    r = Client().post(
        "/api/oauth/revoke_token/",
        {"token": t["refresh_token"], "token_type_hint": "refresh_token", "client_id": "gastos-cli"},
    )
    assert r.status_code == 200
    assert refrescar(t["refresh_token"]).json()["error"] == "invalid_grant"
    assert Client().get("/api/oauth/userinfo/", HTTP_AUTHORIZATION=f"Bearer {t['access_token']}").status_code == 401


def test_un_cliente_no_revoca_los_tokens_de_otro(cli, ana):
    registrar("otra-app", redirect_uris=("https://otra.example.com/callback",))
    t = tokens(ana)
    r = Client().post("/api/oauth/revoke_token/", {"token": t["refresh_token"], "client_id": "otra-app"})
    assert r.status_code == 200  # RFC 7009 §2.2: siempre 200, no revela si el token existe…
    assert refrescar(t["refresh_token"]).status_code == 200  # …pero no lo ha revocado


# ── Client credentials: un servicio, sin usuario ──
def test_client_credentials(ana):
    monitor = registrar("monitor", tipo=TipoCliente.SERVICIO, scopes="operaciones:leer", redirect_uris=())
    basic = base64.b64encode(f"monitor:{monitor.client_secret}".encode()).decode()
    r = Client().post(
        "/api/oauth/token/",
        {"grant_type": "client_credentials", "scope": "operaciones:leer"},
        HTTP_AUTHORIZATION=f"Basic {basic}",
    )
    assert r.status_code == 200
    t = r.json()
    assert "refresh_token" not in t and "id_token" not in t  # sin usuario: ni refresh ni identidad
    assert AccessToken.objects.get().user is None


def test_client_credentials_exige_el_secreto(ana):
    registrar("monitor", tipo=TipoCliente.SERVICIO, scopes="operaciones:leer", redirect_uris=())
    basic = base64.b64encode(b"monitor:no-es-el-secreto").decode()
    r = Client().post("/api/oauth/token/", {"grant_type": "client_credentials"}, HTTP_AUTHORIZATION=f"Basic {basic}")
    assert r.status_code == 401 and r.json()["error"] == "invalid_client"


def test_un_cliente_nativo_no_puede_usar_client_credentials(cli):
    r = Client().post("/api/oauth/token/", {"grant_type": "client_credentials", "client_id": "gastos-cli"})
    assert r.status_code in (400, 401) and "access_token" not in json.loads(r.content)


def test_el_secreto_se_guarda_con_hash(ana):
    monitor = registrar("monitor", tipo=TipoCliente.SERVICIO, scopes="operaciones:leer", redirect_uris=())
    guardado = Application.objects.get(client_id="monitor").client_secret
    assert guardado != monitor.client_secret and check_password(monitor.client_secret, guardado)  # como una contraseña
