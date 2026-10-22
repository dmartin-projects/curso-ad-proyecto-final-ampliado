"""Los comandos del authorization server (módulo 90)."""

from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.test import Client
from jwcrypto import jwk

from conftest import UsuarioFactory
from oauth.models import ClienteOAuth
from oauth.tests.infrastructure.flujo import peticion, pkce, registrar

pytestmark = pytest.mark.django_db


def test_crear_cliente_nativo():
    salida = StringIO()
    call_command(
        "crear_cliente_oauth", "gastos-cli", "--tipo", "nativa", "--client-id", "gastos-cli",
        "--scopes", "openid email gastos:leer gastos:escribir", "--redirect-uri", "http://127.0.0.1/callback",
        stdout=salida,
    )  # fmt: skip
    assert salida.getvalue() == "client_id: gastos-cli\n"  # sin secreto: es un public client
    assert ClienteOAuth.objects.get().scopes == ["email", "gastos:escribir", "gastos:leer", "openid"]


def test_crear_un_servicio_enseña_el_secreto_una_vez():
    salida = StringIO()
    call_command("crear_cliente_oauth", "Monitor", "--tipo", "servicio", "--scopes", "operaciones:leer", stdout=salida)
    lineas = salida.getvalue().splitlines()
    assert lineas[0].startswith("client_id: ") and lineas[1].startswith("client_secret: ")
    assert "no se puede volver a ver" in lineas[2]


def test_crear_cliente_con_reglas_que_no_cumple():
    with pytest.raises(CommandError, match="http solo a 127.0.0.1"):
        call_command("crear_cliente_oauth", "Web", "--tipo", "web", "--scopes", "openid",
                     "--redirect-uri", "http://app.example.com/callback")  # fmt: skip


def test_generar_clave_oidc():
    salida = StringIO()
    call_command("generar_clave_oidc", stdout=salida)
    linea = salida.getvalue().strip()
    assert linea.startswith('OIDC_RSA_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\n') and "\n" not in linea
    pem = linea.split("=", 1)[1].strip('"').replace("\\n", "\n")
    assert jwk.JWK.from_pem(pem.encode())["kty"] == "RSA"


def test_no_eres_tu():
    """En la pantalla de consentimiento, "Entra con otra cuenta" cierra la sesión del authorization server y vuelve
    al login con la misma petición."""
    registrar()
    navegador = Client()
    navegador.force_login(UsuarioFactory())
    _, challenge = pkce()
    pantalla = navegador.get("/api/oauth/authorize/", peticion(challenge))
    siguiente = pantalla.context["request"].get_full_path()
    r = navegador.post("/api/oauth/salir/", {"next": f"/api/oauth/login/?next={siguiente}"})
    assert r.status_code == 302 and r.headers["Location"].startswith("/api/oauth/login/?next=/api/oauth/authorize/")
    assert navegador.get("/api/oauth/authorize/", peticion(challenge)).status_code == 302  # ya sin sesión
