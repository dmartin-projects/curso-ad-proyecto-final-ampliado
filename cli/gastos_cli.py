# /// script
# requires-python = ">=3.13"
# dependencies = ["httpx>=0.28", "pyjwt[crypto]>=2.10", "keyring>=25"]
# ///
"""gastos-cli: un cliente OAuth 2.1 + OpenID Connect escrito "a mano" para la API de Gastos (módulo 90).

Es una app NATIVA (RFC 8252): un public client, sin secreto (cualquiera puede leer este archivo). Por eso:
  - authorization code + PKCE (S256): el code solo lo puede canjear quien tiene el code_verifier;
  - el navegador del sistema para el login (la contraseña nunca pasa por aquí) y la vuelta a un servidor de
    loopback en 127.0.0.1 con un puerto efímero;
  - state (CSRF en la vuelta), iss (RFC 9207, mix-up) y nonce (el ID token es de ESTA petición);
  - el ID token se valida entero: firma con la clave del JWKS (por su kid), alg, iss, aud, exp, iat y nonce;
  - el refresh token, en el llavero del sistema (keyring) o, si no hay, en un archivo con permisos 600.

Uso:  uv run cli/gastos_cli.py login | hogares | movimientos 3 | gasto 3 --cuenta 5 --importe -12.50 --concepto Pan
      | quien | logout          (GASTOS_EMISOR=https://gastos.tudominio.com/api/oauth para producción)
"""

import argparse
import base64
import hashlib
import hmac
import http.server
import json
import os
import secrets
import sys
import webbrowser
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx
import jwt

CLIENT_ID = "gastos-cli"  # público: identifica a la app, no la autentica
SCOPES = "openid email gastos:leer gastos:escribir"
EMISOR = os.environ.get("GASTOS_EMISOR", "http://localhost:8000/api/oauth")
ESPERA_LOGIN = 300  # segundos para completar el login en el navegador


class ErrorOAuth(Exception):
    pass


# ── Discovery ──
def descubrir(http: httpx.Client, emisor: str) -> dict:
    meta = http.get(f"{emisor}/.well-known/openid-configuration").raise_for_status().json()
    if meta["issuer"] != emisor:  # OIDC Discovery §4.3: idéntico, o alguien nos está dando los endpoints de otro
        raise ErrorOAuth(f"El discovery dice issuer={meta['issuer']!r}, no {emisor!r}.")
    return meta


# ── PKCE (RFC 7636) ──
def pkce() -> tuple[str, str]:
    """(code_verifier, code_challenge). El verifier se queda aquí; al servidor solo va su SHA-256."""
    verifier = secrets.token_urlsafe(64)  # 86 caracteres: entre 43 y 128
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


# ── La vuelta del navegador: un servidor de loopback para UNA petición ──
class _Vuelta(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (el nombre lo pone http.server)
        partes = urlsplit(self.path)
        if partes.path != "/callback":
            self.send_error(404)
            return
        self.server.parametros = {k: v[0] for k, v in parse_qs(partes.query).items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Referrer-Policy", "no-referrer")  # que el code no salga en un Referer
        self.end_headers()
        self.wfile.write("<p>Listo. Ya puedes cerrar esta pestaña y volver a la terminal.</p>".encode())

    def log_message(self, *args):  # sin ruido en la terminal (y sin el code en ningún log)
        pass


def abrir_vuelta() -> http.server.HTTPServer:
    servidor = http.server.HTTPServer(("127.0.0.1", 0), _Vuelta)  # puerto 0: el sistema elige uno libre
    servidor.parametros = None
    servidor.timeout = ESPERA_LOGIN
    return servidor


def comprobar_vuelta(parametros: dict | None, *, state: str, emisor: str) -> str:
    """El code, si la vuelta es la respuesta a NUESTRA petición y de NUESTRO servidor."""
    if parametros is None:
        raise ErrorOAuth("No ha llegado la respuesta del navegador a tiempo.")
    if not hmac.compare_digest(parametros.get("state", ""), state):
        raise ErrorOAuth("El state no coincide: esta respuesta no es de nuestra petición (¿CSRF?).")
    if parametros.get("iss") != emisor:  # RFC 9207: quién envía la respuesta (ataque mix-up)
        raise ErrorOAuth(f"La respuesta viene de {parametros.get('iss')!r}, no de {emisor!r}.")
    if "error" in parametros:
        raise ErrorOAuth(f"El servidor dice {parametros['error']}: {parametros.get('error_description', '')}")
    return parametros["code"]


# ── El ID token (OIDC Core §3.1.3.7) ──
def validar_id_token(id_token: str, *, jwks: dict, emisor: str, client_id: str, nonce: str) -> dict:
    cabecera = jwt.get_unverified_header(id_token)
    if cabecera.get("alg") != "RS256":
        # Nunca "none" (sin firma) ni HS256 (alguien que firma con la clave PÚBLICA como si fuera un secreto)
        raise ErrorOAuth(f"Algoritmo no permitido: {cabecera.get('alg')!r}.")
    clave = next((k for k in jwks.get("keys", []) if k.get("kid") == cabecera.get("kid")), None)
    if clave is None:
        raise ErrorOAuth(f"Ninguna clave del JWKS tiene el kid {cabecera.get('kid')!r}.")
    try:
        claims = jwt.decode(
            id_token,
            key=jwt.PyJWK(clave).key,
            algorithms=["RS256"],  # la lista blanca, otra vez: la librería no decide por la cabecera
            audience=client_id,  # aud: el token es para ESTA app (uno para otra app no vale aquí)
            issuer=emisor,
            options={"require": ["iss", "sub", "aud", "exp", "iat"]},
            leeway=30,  # segundos de margen por relojes desajustados
        )
    except jwt.PyJWTError as e:
        raise ErrorOAuth(f"ID token no válido: {e}") from e
    if not hmac.compare_digest(claims.get("nonce", ""), nonce):
        raise ErrorOAuth("El nonce no coincide: este ID token no es de esta petición (¿replay?).")
    return claims


def jwks_con_kid(http: httpx.Client, meta: dict, id_token: str) -> dict:
    """El JWKS; si no trae el kid del token, se vuelve a pedir UNA vez (el servidor puede haber rotado la clave)."""
    jwks = http.get(meta["jwks_uri"]).raise_for_status().json()
    kid = jwt.get_unverified_header(id_token).get("kid")
    if not any(k.get("kid") == kid for k in jwks.get("keys", [])):
        jwks = http.get(meta["jwks_uri"], headers={"Cache-Control": "no-cache"}).raise_for_status().json()
    return jwks


# ── Dónde se guarda el refresh token ──
class AlmacenArchivo:
    """Un JSON {emisor: refresh_token} legible solo por tu usuario (600), en un directorio 700."""

    def __init__(self, ruta: Path):
        self.ruta = ruta

    def _todo(self) -> dict:
        return json.loads(self.ruta.read_text()) if self.ruta.exists() else {}

    def leer(self, emisor: str) -> str | None:
        return self._todo().get(emisor)

    def guardar(self, emisor: str, token: str) -> None:
        self._escribir(self._todo() | {emisor: token})

    def borrar(self, emisor: str) -> None:
        datos = self._todo()
        if datos.pop(emisor, None) is not None:
            self._escribir(datos)

    def _escribir(self, datos: dict) -> None:
        self.ruta.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # O_CREAT con 0o600: el archivo NACE con esos permisos (un chmod después dejaría un instante abierto)
        fd = os.open(self.ruta, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(datos, f)
        os.chmod(self.ruta, 0o600)  # por si ya existía con otros permisos


class AlmacenLlavero:
    """El llavero del sistema (Keychain en macOS, Credential Manager en Windows, Secret Service en Linux)."""

    def __init__(self, keyring):
        self.keyring = keyring

    def leer(self, emisor):
        return self.keyring.get_password("gastos-cli", emisor)

    def guardar(self, emisor, token):
        self.keyring.set_password("gastos-cli", emisor, token)

    def borrar(self, emisor):
        try:
            self.keyring.delete_password("gastos-cli", emisor)
        except self.keyring.errors.PasswordDeleteError:
            pass


def almacen_por_defecto():
    try:
        import keyring
        from keyring.backends.fail import Keyring as SinLlavero
    except ImportError:
        keyring = None
    if keyring is not None and not isinstance(keyring.get_keyring(), SinLlavero):
        return AlmacenLlavero(keyring)
    ruta = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "gastos-cli" / "tokens.json"
    print(f"(sin llavero del sistema: el refresh token se guarda en {ruta}, con permisos 600)", file=sys.stderr)
    return AlmacenArchivo(ruta)


# ── Los flujos ──
def login(http: httpx.Client, almacen, *, emisor: str = EMISOR, scopes: str = SCOPES, abrir=webbrowser.open) -> dict:
    meta = descubrir(http, emisor)
    state, nonce = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    verifier, challenge = pkce()
    vuelta = abrir_vuelta()
    redirect_uri = f"http://127.0.0.1:{vuelta.server_port}/callback"
    url = (
        meta["authorization_endpoint"]
        + "?"
        + urlencode(
            {
                "response_type": "code",
                "client_id": CLIENT_ID,
                "redirect_uri": redirect_uri,
                "scope": scopes,
                "state": state,
                "nonce": nonce,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            }
        )
    )
    print(f"Abriendo el navegador para entrar en Gastos. Si no se abre, ve a:\n{url}", file=sys.stderr)
    abrir(url)
    vuelta.handle_request()  # espera a UNA petición (o al timeout)
    vuelta.server_close()
    code = comprobar_vuelta(vuelta.parametros, state=state, emisor=emisor)

    r = http.post(
        meta["token_endpoint"],
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,  # la misma de la petición: el servidor lo comprueba
            "client_id": CLIENT_ID,
            "code_verifier": verifier,  # la prueba de que esta app es la que empezó el flujo
        },
    )
    if r.status_code != 200:
        raise ErrorOAuth(f"No se pudo canjear el code: {r.text}")
    tokens = r.json()
    claims = validar_id_token(
        tokens["id_token"], jwks=jwks_con_kid(http, meta, tokens["id_token"]), emisor=emisor, client_id=CLIENT_ID,
        nonce=nonce,
    )  # fmt: skip
    almacen.guardar(emisor, tokens["refresh_token"])  # el access token NO se guarda: vive lo que dura el comando
    return claims


def access_token(http: httpx.Client, almacen, *, emisor: str = EMISOR) -> str:
    """Un access token nuevo con el refresh token guardado, que ROTA: se guarda el nuevo (el viejo ya no vale)."""
    refresh = almacen.leer(emisor)
    if refresh is None:
        raise ErrorOAuth("No has entrado: gastos-cli login")
    meta = descubrir(http, emisor)
    r = http.post(
        meta["token_endpoint"], data={"grant_type": "refresh_token", "refresh_token": refresh, "client_id": CLIENT_ID}
    )
    if r.status_code == 400 and r.json().get("error") == "invalid_grant":
        almacen.borrar(emisor)
        raise ErrorOAuth("La sesión ha caducado o se ha revocado: gastos-cli login")
    r.raise_for_status()
    tokens = r.json()
    almacen.guardar(emisor, tokens["refresh_token"])
    return tokens["access_token"]


def logout(http: httpx.Client, almacen, *, emisor: str = EMISOR) -> None:
    """Revoca el refresh token en el servidor (RFC 7009) y lo borra de aquí. Revocarlo revoca su familia."""
    refresh = almacen.leer(emisor)
    if refresh is not None:
        meta = descubrir(http, emisor)
        data = {"token": refresh, "token_type_hint": "refresh_token", "client_id": CLIENT_ID}
        http.post(meta["revocation_endpoint"], data=data).raise_for_status()
    almacen.borrar(emisor)


def api_base(emisor: str) -> str:
    return emisor.removesuffix("/oauth") + "/v1"  # https://…/api/oauth → https://…/api/v1


def llamar(http: httpx.Client, almacen, metodo: str, ruta: str, *, emisor: str = EMISOR, **kwargs) -> httpx.Response:
    token = access_token(http, almacen, emisor=emisor)
    r = http.request(metodo, api_base(emisor) + ruta, headers={"Authorization": f"Bearer {token}"}, **kwargs)
    if r.status_code in (401, 403):
        raise ErrorOAuth(f"{r.status_code}: {r.json().get('detail')} ({r.headers.get('WWW-Authenticate', '')})")
    return r.raise_for_status()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="gastos-cli", description="Gastos desde la terminal (OAuth 2.1 + OIDC)")
    sub = p.add_subparsers(dest="orden", required=True)
    sub.add_parser("login")
    sub.add_parser("logout")
    sub.add_parser("quien")
    sub.add_parser("hogares")
    m = sub.add_parser("movimientos")
    m.add_argument("hogar", type=int)
    g = sub.add_parser("gasto")
    g.add_argument("hogar", type=int)
    g.add_argument("--cuenta", type=int, required=True)
    g.add_argument("--importe", required=True, help="negativo para un gasto: -12.50")
    g.add_argument("--concepto", required=True)
    g.add_argument("--fecha", default=None, help="AAAA-MM-DD (hoy, si no)")
    args = p.parse_args(argv)

    almacen = almacen_por_defecto()
    with httpx.Client(timeout=10) as http:
        try:
            match args.orden:
                case "login":
                    claims = login(http, almacen)
                    print(f"Has entrado como {claims.get('email', claims['sub'])}.")
                case "logout":
                    logout(http, almacen)
                    print("Sesión cerrada (y revocada en el servidor).")
                case "quien":
                    token = access_token(http, almacen)
                    meta = descubrir(http, EMISOR)
                    r = http.get(meta["userinfo_endpoint"], headers={"Authorization": f"Bearer {token}"})
                    print(json.dumps(r.raise_for_status().json(), indent=2, ensure_ascii=False))
                case "hogares":
                    for h in llamar(http, almacen, "GET", "/hogares/").json()["results"]:
                        print(f"{h['id']:>4}  {h['nombre']}  ({h['mi_rol']})")
                case "movimientos":
                    for mov in llamar(http, almacen, "GET", f"/hogares/{args.hogar}/movimientos/").json()["results"]:
                        print(f"{mov['fecha']}  {mov['importe']:>10}  {mov['concepto']}")
                case "gasto":
                    datos = {
                        "cuenta": args.cuenta,
                        "importe": args.importe,
                        "concepto": args.concepto,
                        "fecha": args.fecha or date.today().isoformat(),
                    }
                    mov = llamar(http, almacen, "POST", f"/hogares/{args.hogar}/movimientos/", json=datos).json()
                    print(f"Apuntado: {mov['fecha']} {mov['importe']} {mov['concepto']} (id {mov['id']})")
        except ErrorOAuth as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
