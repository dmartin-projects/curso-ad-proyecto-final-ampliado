"""gastos-cli (cli/gastos_cli.py) contra el servidor de verdad (live_server), y sus defensas una a una (módulo 90)."""

import base64
import hashlib
import hmac
import importlib.util
import json
import stat
import threading
import time
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

import httpx
import jwt
import pytest
from django.conf import settings as ajustes
from jwcrypto import jwk

from conftest import CuentaFactory, HogarFactory, MembresiaFactory, UsuarioFactory
from finanzas.models import Movimiento
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.infrastructure.crypto.claves import nueva_clave_pem
from oauth.tests.infrastructure.flujo import registrar

_ruta = Path(ajustes.BASE_DIR).parent / "cli" / "gastos_cli.py"
_spec = importlib.util.spec_from_file_location("gastos_cli", _ruta)
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)


# ── El servidor de verdad y un "navegador" que hace lo que haría la persona ──
@pytest.fixture
def emisor(live_server, settings, transactional_db):
    emisor = f"{live_server.url}/api/oauth"
    settings.OAUTH2_PROVIDER = {**settings.OAUTH2_PROVIDER, "OIDC_ISS_ENDPOINT": emisor}
    registrar()  # gastos-cli, con http://127.0.0.1/callback
    return emisor


@pytest.fixture
def ana(transactional_db):
    ana = UsuarioFactory(email="ana@example.com")
    hogar = HogarFactory(nombre="Casa")
    MembresiaFactory(hogar=hogar, usuario=ana, rol="miembro")
    return ana, hogar, CuentaFactory(hogar=hogar, nombre="Común")


@pytest.fixture
def almacen(tmp_path):
    return cli.AlmacenArchivo(tmp_path / "gastos-cli" / "tokens.json")


class Formularios(HTMLParser):
    """Los <input> de cada <form> de una página: lo que el navegador enviaría."""

    def __init__(self):
        super().__init__()
        self.formularios, self._actual = [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._actual = {"action": a.get("action"), "campos": {}}
            self.formularios.append(self._actual)
        elif tag == "input" and self._actual is not None and a.get("name"):
            self._actual["campos"][a["name"]] = a.get("value") or ""


def campos(html: str, indice=0) -> dict:
    p = Formularios()
    p.feed(html)
    return p.formularios[indice]["campos"]


def navegador(password="clave-segura-123", permitir=True):
    """La persona: abre la URL, entra con su contraseña y pulsa Permitir (o Cancelar). En otro hilo, como el navegador
    de verdad, mientras el CLI espera en su servidor de loopback."""

    def recorrer(url):
        with httpx.Client(follow_redirects=True, timeout=10) as nav:
            login = nav.get(url)  # → el login del authorization server
            datos = campos(login.text) | {"username": "ana@example.com", "password": password}
            consentimiento = nav.post(str(login.url), data=datos)  # → la pantalla de consentimiento
            datos = campos(consentimiento.text)
            if permitir:
                datos["allow"] = "on"
            nav.post(str(consentimiento.url), data=datos)  # → 302 a http://127.0.0.1:<puerto>/callback (el CLI)

    return lambda url: threading.Thread(target=recorrer, args=(url,), daemon=True).start()


def atacante(**vuelta):
    """Alguien que llama al servidor de loopback del CLI con lo que le conviene (un code suyo, otro state…)."""

    def llamar(url):
        params = dict(httpx.URL(url).params)
        destino = httpx.URL(params["redirect_uri"]).copy_merge_params(
            {k: (params[v[1:]] if isinstance(v, str) and v.startswith("=") else v) for k, v in vuelta.items()}
        )
        threading.Thread(target=lambda: (time.sleep(0.1), httpx.get(str(destino))), daemon=True).start()

    return llamar


# ── El recorrido completo ──
def test_login_y_la_api_desde_la_terminal(emisor, ana, almacen):
    usuario, hogar, cuenta = ana
    with httpx.Client(timeout=10) as http:
        claims = cli.login(http, almacen, emisor=emisor, abrir=navegador())
        assert claims["email"] == "ana@example.com" and claims["aud"] == "gastos-cli"

        # El refresh token, guardado y solo para ti
        ruta = almacen.ruta
        assert stat.S_IMODE(ruta.stat().st_mode) == 0o600 and stat.S_IMODE(ruta.parent.stat().st_mode) == 0o700
        client_id, primero = cli.leer_sesion(almacen, emisor)
        assert client_id == "gastos-cli" and primero.startswith("gst_rt_")

        # Cada orden pide un access token nuevo con el refresh token, que rota
        hogares = cli.llamar(http, almacen, "GET", "/hogares/", emisor=emisor).json()["results"]
        assert [h["nombre"] for h in hogares] == ["Casa"]
        assert cli.leer_sesion(almacen, emisor)[1] != primero

        datos = {"cuenta": cuenta.pk, "importe": "-3.20", "concepto": "Café", "fecha": "2026-10-20"}
        r = cli.llamar(http, almacen, "POST", f"/hogares/{hogar.pk}/movimientos/", emisor=emisor, json=datos)
        assert Movimiento.objects.get(pk=r.json()["id"]).creado_por == usuario

        # Cerrar sesión revoca en el servidor: el refresh token ya no sirve ni aunque alguien lo hubiera copiado
        _, copiado = cli.leer_sesion(almacen, emisor)
        cli.logout(http, almacen, emisor=emisor)
        assert almacen.leer(emisor) is None
        r = http.post(
            f"{emisor}/token/",
            data={"grant_type": "refresh_token", "refresh_token": copiado, "client_id": "gastos-cli"},
        )
        assert r.json()["error"] == "invalid_grant"
        with pytest.raises(cli.ErrorOAuth, match="No has entrado"):
            cli.access_token(http, almacen, emisor=emisor)


def test_si_la_persona_cancela(emisor, ana, almacen):
    with httpx.Client(timeout=10) as http, pytest.raises(cli.ErrorOAuth, match="access_denied"):
        cli.login(http, almacen, emisor=emisor, abrir=navegador(permitir=False))
    assert almacen.leer(emisor) is None


def test_una_vuelta_con_otro_state_se_rechaza(emisor, ana, almacen):
    """CSRF en la vuelta: alguien intenta colarle al CLI un code SUYO (el usuario acabaría en la cuenta del atacante)."""
    with httpx.Client(timeout=10) as http, pytest.raises(cli.ErrorOAuth, match="state no coincide"):
        cli.login(http, almacen, emisor=emisor, abrir=atacante(code="code-del-atacante", state="otro", iss=emisor))


def test_una_vuelta_de_otro_servidor_se_rechaza(emisor, ana, almacen):
    """Mix-up (RFC 9207): la respuesta trae un iss que no es el del servidor al que se le pidió."""
    malo = "https://atacante.example.com"
    with httpx.Client(timeout=10) as http, pytest.raises(cli.ErrorOAuth, match="atacante"):
        cli.login(http, almacen, emisor=emisor, abrir=atacante(code="x", state="=state", iss=malo))


def test_la_sesion_revocada_en_el_servidor(emisor, ana, almacen):
    with httpx.Client(timeout=10) as http:
        cli.login(http, almacen, emisor=emisor, abrir=navegador())
        _, refresh = cli.leer_sesion(almacen, emisor)
        http.post(f"{emisor}/revoke_token/", data={"token": refresh, "client_id": "gastos-cli"})
        with pytest.raises(cli.ErrorOAuth, match="caducado o se ha revocado"):
            cli.access_token(http, almacen, emisor=emisor)
        assert almacen.leer(emisor) is None


def test_un_discovery_de_otro_emisor_se_rechaza():
    """El documento de discovery dice quién es el emisor: si no es el que pedimos, sus endpoints no son de fiar."""
    otro = httpx.MockTransport(lambda r: httpx.Response(200, json={"issuer": "https://atacante.example.com"}))
    with httpx.Client(transport=otro) as http, pytest.raises(cli.ErrorOAuth, match="issuer"):
        cli.descubrir(http, "https://gastos.example.com/api/oauth")


# ── El ID token, uno a uno (sin servidor) ──
EMISOR, CLIENTE, NONCE = "https://gastos.example.com/api/oauth", "gastos-cli", "n-123"


@pytest.fixture(scope="module")
def clave():
    pem = nueva_clave_pem()
    publica = jwk.JWK.from_pem(pem.encode())
    return pem, {"keys": [json.loads(publica.export_public()) | {"kid": "k1", "alg": "RS256", "use": "sig"}]}


def firmar(pem, kid="k1", **cambios):
    ahora = int(time.time())
    claims = {"iss": EMISOR, "aud": CLIENTE, "sub": "1", "iat": ahora, "exp": ahora + 600, "nonce": NONCE} | cambios
    return jwt.encode({k: v for k, v in claims.items() if v is not None}, pem, algorithm="RS256", headers={"kid": kid})


def validar(token, jwks):
    return cli.validar_id_token(token, jwks=jwks, emisor=EMISOR, client_id=CLIENTE, nonce=NONCE)


def test_un_id_token_valido(clave):
    pem, jwks = clave
    assert validar(firmar(pem), jwks)["sub"] == "1"


@pytest.mark.parametrize(
    "cambios, error",
    [
        ({"aud": "otra-app"}, "Audience"),  # un token emitido para otra app
        ({"iss": "https://otro.example.com"}, "issuer"),
        ({"exp": int(time.time()) - 120}, "expired"),
        ({"nonce": "otro"}, "nonce"),  # replay: un ID token de otra petición
        ({"nonce": None}, "nonce"),
        ({"iat": None}, "iat"),
    ],
)
def test_claims_que_no_cuadran(clave, cambios, error):
    pem, jwks = clave
    with pytest.raises(cli.ErrorOAuth, match=error):
        validar(firmar(pem, **cambios), jwks)


def _b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def _a_mano(cabecera: dict, claims: dict, firma: bytes = b"") -> str:
    inicio = f"{_b64(json.dumps(cabecera).encode())}.{_b64(json.dumps(claims).encode())}"
    return f"{inicio}.{_b64(firma)}"


def test_alg_none_se_rechaza(clave):
    _, jwks = clave
    claims = jwt.decode(firmar(clave[0]), options={"verify_signature": False})
    with pytest.raises(cli.ErrorOAuth, match="Algoritmo no permitido"):
        validar(_a_mano({"alg": "none", "kid": "k1"}, claims), jwks)


def test_hs256_firmado_con_la_clave_publica_se_rechaza(clave):
    """Confusión de algoritmos: el atacante firma con HMAC usando la clave PÚBLICA (que todo el mundo tiene). Un
    cliente que eligiera el algoritmo por la cabecera la daría por buena."""
    pem, jwks = clave
    publica = jwk.JWK.from_pem(pem.encode()).export_to_pem().decode()  # la pública en PEM
    claims = jwt.decode(firmar(pem), options={"verify_signature": False})
    cabecera = {"alg": "HS256", "kid": "k1"}
    sin_firma = _a_mano(cabecera, claims).rsplit(".", 1)[0]
    firma = hmac.new(publica.encode(), sin_firma.encode(), hashlib.sha256).digest()
    with pytest.raises(cli.ErrorOAuth, match="Algoritmo no permitido"):
        validar(f"{sin_firma}.{_b64(firma)}", jwks)


def test_un_kid_desconocido_o_una_firma_de_otra_clave(clave):
    pem, jwks = clave
    with pytest.raises(cli.ErrorOAuth, match="kid"):
        validar(firmar(pem, kid="k2"), jwks)
    with pytest.raises(cli.ErrorOAuth, match="Signature"):
        validar(firmar(nueva_clave_pem(), kid="k1"), jwks)  # el kid de la buena, firmado con otra


def test_el_almacen_sin_llavero_es_un_archivo_600(tmp_path):
    almacen = cli.AlmacenArchivo(tmp_path / "dir" / "tokens.json")
    almacen.guardar("https://a", "gst_rt_1")
    almacen.guardar("https://b", "gst_rt_2")
    almacen.borrar("https://a")
    assert (almacen.leer("https://a"), almacen.leer("https://b")) == (None, "gst_rt_2")
    assert stat.S_IMODE(almacen.ruta.stat().st_mode) == 0o600


def test_si_el_kid_no_esta_en_el_jwks_se_vuelve_a_pedir_una_vez(clave):
    """Ejercicio 2: el servidor ha rotado su clave y el JWKS que teníamos (de una caché) aún no trae la nueva."""
    pem, jwks_nuevo = clave
    peticiones = []

    def servidor(request):
        peticiones.append(request.headers.get("Cache-Control"))
        return httpx.Response(200, json={"keys": []} if len(peticiones) == 1 else jwks_nuevo)

    with httpx.Client(transport=httpx.MockTransport(servidor)) as http:
        jwks = cli.jwks_con_kid(http, {"jwks_uri": "https://gastos.example.com/jwks"}, firmar(pem))
    assert jwks == jwks_nuevo and peticiones == [None, "no-cache"]


# ── Ejercicio 3: login --dispositivo (device authorization grant) ──
def test_login_desde_un_dispositivo_sin_navegador(emisor, ana, almacen, time_machine):
    registrar(
        "gastos-cli-dispositivo", tipo=TipoCliente.DISPOSITIVO, scopes="gastos:leer gastos:escribir", redirect_uris=()
    )
    time_machine.move_to(datetime.now(UTC), tick=True)  # el reloj sigue corriendo; dormir() lo adelanta
    mensajes, personas = [], []

    def avisar(mensaje):  # la terminal enseña el código; la persona lo escribe en su móvil (otro hilo)
        mensajes.append(mensaje)
        codigo = mensaje.rsplit(" ", 1)[1]

        def en_el_movil():
            with httpx.Client(follow_redirects=True, timeout=10) as nav:
                login = nav.get(f"{emisor}/device/")
                datos = campos(login.text) | {"username": "ana@example.com", "password": "clave-segura-123"}
                pantalla = nav.post(str(login.url), data=datos)
                confirmar = nav.post(str(pantalla.url), data=campos(pantalla.text) | {"user_code": codigo})
                nav.post(str(confirmar.url), data=campos(confirmar.text) | {"action": "accept"})

        personas.append(threading.Thread(target=en_el_movil, daemon=True))
        personas[-1].start()

    def dormir(segundos):  # el reloj del servidor avanza lo que el CLI espera (sin esperar de verdad)
        personas[-1].join(timeout=10)  # (y la persona termina antes de la segunda pregunta)
        time_machine.shift(segundos)

    with httpx.Client(timeout=10) as http:
        cli.login_dispositivo(http, almacen, emisor=emisor, dormir=dormir, avisar=avisar)
        assert "/api/oauth/device/ y escribe el código " in mensajes[0]
        assert cli.leer_sesion(almacen, emisor)[0] == "gastos-cli-dispositivo"
        hogares = cli.llamar(http, almacen, "GET", "/hogares/", emisor=emisor).json()[
            "results"
        ]  # renueva con SU cliente
        assert [h["nombre"] for h in hogares] == ["Casa"]


@pytest.mark.parametrize(
    "errores, mensaje",
    [(["slow_down", "access_denied"], "Has cancelado"), (["authorization_pending", "expired_token"], "caducado")],
)
def test_login_desde_un_dispositivo_errores(errores, mensaje):
    """El servidor dice que espere más (slow_down: +5 s), que todavía no (authorization_pending) o que no."""
    pendientes, esperas = list(errores), []

    def servidor(request):
        if request.url.path.endswith("openid-configuration"):
            return httpx.Response(200, json={"issuer": "https://g/api/oauth", "device_authorization_endpoint":
                                             "https://g/d", "token_endpoint": "https://g/t"})  # fmt: skip
        if request.url.path == "/d":
            return httpx.Response(200, json={"device_code": "x", "user_code": "ABCDEFGH", "verification_uri": "v",
                                             "interval": 5, "expires_in": 600})  # fmt: skip
        return httpx.Response(400, json={"error": pendientes.pop(0)})

    with httpx.Client(transport=httpx.MockTransport(servidor)) as http, pytest.raises(cli.ErrorOAuth, match=mensaje):
        cli.login_dispositivo(http, None, emisor="https://g/api/oauth", dormir=esperas.append, avisar=lambda m: None)
    assert esperas == ([5, 10] if errores[0] == "slow_down" else [5, 5])
