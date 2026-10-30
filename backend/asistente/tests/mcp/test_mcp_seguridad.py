"""Módulo 104: lo que la especificación de MCP (2026-07-28) y los RFC de OAuth piden al servidor de Gastos más allá de
"un token válido": el recurso consentido (RFC 8707), los desafíos WWW-Authenticate (RFC 6750), la jerarquía de scopes,
el descubrimiento del authorization server (RFC 8414) y el servidor dentro del ciclo de vida de Django."""

import asyncio
import json
import re
import threading
import time
from pathlib import Path

import httpx2
import pytest
from django.conf import settings
from django.db import connection
from django.test import Client

from asistente.application.tools.resumen_mes_tool import ResumenMesTool
from asistente.infrastructure.api.mcp.aplicacion_mcp import crear_aplicacion_mcp
from asistente.tests.mcp.conftest import URL, VERSION, mcp, token
from oauth.domain.services.scopes import con_implicados
from oauth.infrastructure.api.authentication.token_de_recurso import canonica
from oauth.tests.infrastructure.flujo import canjear, con_sesion, consentir, peticion, pkce, refrescar, vuelta

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.usefixtures("cliente_cli")]
RAIZ = Path(__file__).resolve().parents[4]
LLAMADA = {"name": "resumen_mes", "arguments": {"hogar": None, "mes": "2026-09"}}


def _llamada(hogar) -> dict:
    return {**LLAMADA, "arguments": {**LLAMADA["arguments"], "hogar": hogar.pk}}


# ── WWW-Authenticate (RFC 6750 §3.1 y MCP) ──
def test_sin_credenciales_el_401_no_lleva_codigo_de_error_y_dice_el_scope():
    h = mcp("tools/list").headers["WWW-Authenticate"]
    assert "error=" not in h and 'scope="gastos:leer"' in h and "resource_metadata=" in h


def test_con_un_token_que_no_vale_el_401_dice_invalid_token():
    r = mcp("tools/list", token="gat_no_existe")
    assert r.status_code == 401 and 'error="invalid_token"' in r.headers["WWW-Authenticate"]


def test_el_403_dice_que_scope_hace_falta(casa):
    ana, _ = casa
    h = mcp("tools/list", token=token(ana, scope="openid email")).headers["WWW-Authenticate"]
    assert 'error="insufficient_scope"' in h and 'scope="gastos:leer"' in h


# ── Scopes: quien puede escribir puede leer ──
def test_un_token_con_gastos_escribir_lee():
    assert con_implicados(["openid", "gastos:escribir"]) == {"openid", "gastos:escribir", "gastos:leer"}
    assert con_implicados(["openid", "email"]) == {"openid", "email"}


def test_jerarquia_de_scopes_en_el_servidor(casa):
    ana, _ = casa
    assert mcp("tools/list", token=token(ana, scope="openid gastos:escribir")).status_code == 200


# ── El recurso (RFC 8707) ──
def test_el_recurso_se_compara_exacto_despues_de_normalizarlo(casa):
    assert canonica("HTTP://TESTSERVER:80/api/mcp/") == "http://testserver/api/mcp"
    assert canonica("https://x.example/api/MCP") == "https://x.example/api/MCP"  # la ruta, tal cual
    ana, _ = casa
    assert mcp("tools/list", token=token(ana, resource="HTTP://TESTSERVER/api/mcp")).status_code == 200
    assert mcp("tools/list", token=token(ana, resource="http://testserver/api/mcp/otro")).status_code == 401


def test_un_recurso_que_no_se_pidio_al_autorizar_no_se_concede_en_el_canje(casa):
    """La persona consintió sin ver «Solo en: …/api/mcp»: pedirlo después es invalid_target."""
    ana, _ = casa
    navegador = con_sesion(ana)
    verifier, challenge = pkce()
    code = vuelta(consentir(navegador, peticion(challenge)))["code"]
    r = canjear(code, verifier, resource=URL)
    assert r.status_code == 400 and r.json()["error"] == "invalid_target"


def test_el_refresh_de_un_token_sin_recurso_no_sube_a_mcp(casa):
    ana, _ = casa
    verifier, challenge = pkce()
    code = vuelta(consentir(con_sesion(ana), peticion(challenge, scope="openid gastos:leer")))["code"]
    rt = canjear(code, verifier).json()["refresh_token"]
    r = Client().post(
        "/api/oauth/token/",
        {"grant_type": "refresh_token", "refresh_token": rt, "client_id": "gastos-cli", "resource": URL},
    )
    assert r.status_code == 400 and r.json()["error"] == "invalid_target"
    assert refrescar(rt).status_code == 200  # sin pedir recurso, el refresh de siempre


def test_con_el_recurso_en_la_autorizacion_el_canje_lo_concede(casa):
    ana, _ = casa
    verifier, challenge = pkce()
    code = vuelta(consentir(con_sesion(ana), peticion(challenge, resource=URL)))["code"]
    r = canjear(code, verifier, resource=URL)
    assert r.status_code == 200 and mcp("tools/list", token=r.json()["access_token"]).status_code == 200


# ── Descubrimiento del authorization server (RFC 8414 §3.1) ──
def test_el_metadata_del_authorization_server_donde_lo_busca_un_cliente_mcp():
    """Para el emisor …/api/oauth, el cliente prueba primero con el .well-known delante de la ruta."""
    for ruta in ("/.well-known/oauth-authorization-server/api/oauth", "/.well-known/openid-configuration/api/oauth"):
        r = Client().get(ruta)
        assert r.status_code == 200, ruta
        datos = r.json()
        assert datos["issuer"] == settings.OAUTH_ISSUER and datos["code_challenge_methods_supported"] == ["S256"]


def test_vercel_y_caddy_mandan_a_django_las_urls_de_descubrimiento():
    proxy = json.loads((RAIZ / "frontend" / "vercel.json").read_text())["routes"][0]["src"]
    caddy = (RAIZ / "infra" / "Caddyfile").read_text()
    for ruta in (
        "/.well-known/oauth-protected-resource/api/mcp",
        "/.well-known/oauth-authorization-server/api/oauth",
        "/.well-known/openid-configuration/api/oauth",
    ):
        assert re.match(proxy, ruta), ruta  # si no, Vercel contesta con la SPA: index.html, 200 y text/html
        assert ruta.rsplit("/", 2)[0] + "/*" in caddy, ruta


# ── Dentro del ciclo de vida de Django ──
def test_las_llamadas_no_esperan_en_fila_a_un_solo_hilo(casa, monkeypatch):
    """Tres llamadas a la vez a una tool que tarda 1 s: en paralelo, cada una en su hilo."""
    ana, hogar = casa
    t = token(ana)
    hilos = set()
    original = ResumenMesTool.ejecutar

    def lenta(self, contexto, args):  # como comparar_con_ipc esperando a Eurostat
        hilos.add(threading.get_ident())
        time.sleep(1.0)
        return original(self, contexto, args)

    monkeypatch.setattr(ResumenMesTool, "ejecutar", lenta)

    async def tres():
        app = crear_aplicacion_mcp()
        cuerpo = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            **_llamada(hogar), "_meta": {"io.modelcontextprotocol/protocolVersion": VERSION,
                                         "io.modelcontextprotocol/clientCapabilities": {}}}}  # fmt: skip
        cabeceras = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": VERSION,
                     "Mcp-Method": "tools/call", "Mcp-Name": "resumen_mes", "Authorization": f"Bearer {t}"}  # fmt: skip
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url="http://testserver") as h:
            inicio = time.monotonic()
            rs = await asyncio.gather(*(h.post("/api/mcp", json=cuerpo, headers=cabeceras) for _ in range(3)))
            return time.monotonic() - inicio, [r.status_code for r in rs]

    segundos, codigos = asyncio.run(tres())
    assert codigos == [200, 200, 200] and len(hilos) == 3 and segundos < 2.0


def test_tras_caerse_la_conexion_a_postgresql_el_servidor_se_recupera(casa):
    """Lo que hace un reinicio de PostgreSQL o un failover: cortar las conexiones abiertas."""
    ana, hogar = casa
    t = token(ana)
    assert not mcp("tools/call", _llamada(hogar), token=t).json()["result"]["isError"]
    with connection.cursor() as c:
        c.execute(
            "SELECT count(pg_terminate_backend(pid)) FROM pg_stat_activity "
            "WHERE datname = current_database() AND pid <> pg_backend_pid()"
        )
    r = mcp("tools/call", _llamada(hogar), token=t)
    assert r.status_code == 200 and not r.json()["result"]["isError"]
