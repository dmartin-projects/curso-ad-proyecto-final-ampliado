"""El flujo authorization code + PKCE paso a paso, para los tests (módulo 90). Con el Client de Django: sin navegador."""

import base64
import hashlib
import secrets
from urllib.parse import parse_qs, urlsplit

from django.test import Client

from oauth.application.registrar_cliente_use_case.dtos.registrar_cliente_input_dto import RegistrarClienteInputDTO
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.infrastructure import container

REDIRECT = "http://127.0.0.1/callback"  # la registrada; en cada petición, con un puerto (RFC 8252 §7.3)
REDIRECT_CON_PUERTO = "http://127.0.0.1:53682/callback"
SCOPES_CLI = "openid email profile gastos:leer gastos:escribir"


def registrar(
    client_id="gastos-cli", tipo=TipoCliente.NATIVA, scopes=SCOPES_CLI, redirect_uris=(REDIRECT,), nombre=None
):
    cmd = RegistrarClienteInputDTO(
        nombre or client_id, tipo, frozenset(scopes.split()), tuple(redirect_uris), client_id
    )
    return container.registrar_cliente().ejecutar(cmd)


def pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    return verifier, base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()


def peticion(challenge, **cambios) -> dict:
    """Los parámetros de GET /authorize. `cambios` con valor None quita ese parámetro."""
    params = {
        "response_type": "code",
        "client_id": "gastos-cli",
        "redirect_uri": REDIRECT_CON_PUERTO,
        "scope": "openid email gastos:leer",
        "state": "estado-123",
        "nonce": "nonce-456",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    params.update(cambios)
    return {k: v for k, v in params.items() if v is not None}


def consentir(navegador: Client, params: dict, permitir=True, **trampas):
    """GET /authorize (la pantalla) y POST con lo que lleva el formulario, como haría el navegador.
    `trampas`: campos ocultos del formulario cambiados a mano (lo que podría hacer un usuario malicioso)."""
    pantalla = navegador.get("/api/oauth/authorize/", params)
    assert pantalla.status_code == 200, pantalla.content[:300]
    datos = {k: v for k, v in pantalla.context["form"].initial.items() if v is not None} | trampas
    if permitir:
        datos["allow"] = "on"
    return navegador.post("/api/oauth/authorize/", datos)


def vuelta(respuesta) -> dict:
    """Los parámetros con los que el servidor devuelve al navegador a la redirect URI."""
    assert respuesta.status_code == 302, respuesta.content[:300]
    return {k: v[0] for k, v in parse_qs(urlsplit(respuesta.headers["Location"]).query).items()}


def canjear(code, verifier, redirect_uri=REDIRECT_CON_PUERTO, client_id="gastos-cli", **extra):
    datos = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri, "client_id": client_id}
    if verifier is not None:
        datos["code_verifier"] = verifier
    return Client().post("/api/oauth/token/", datos | extra)


def refrescar(refresh_token, client_id="gastos-cli"):
    datos = {"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": client_id}
    return Client().post("/api/oauth/token/", datos)


def tokens(usuario, scope="openid email gastos:leer", client_id="gastos-cli") -> dict:
    """El flujo entero (el usuario ya ha entrado y consiente): la respuesta del token endpoint."""
    navegador = Client()
    navegador.force_login(usuario)
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge, scope=scope, client_id=client_id)))["code"]
    respuesta = canjear(code, verifier, client_id=client_id)
    assert respuesta.status_code == 200, respuesta.content
    return respuesta.json()
