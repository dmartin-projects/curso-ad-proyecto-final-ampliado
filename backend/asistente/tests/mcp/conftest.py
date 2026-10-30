import asyncio

import httpx2
import pytest

from asistente.infrastructure.api.mcp.aplicacion_mcp import crear_aplicacion_mcp
from oauth.tests.infrastructure.flujo import canjear, con_sesion, consentir, peticion, pkce, registrar, vuelta

URL = "http://testserver/api/mcp"
VERSION = "2026-07-28"


def token(usuario, *, scope="gastos:leer", resource: str | None = URL) -> str:
    """Un access token de Gastos por el flujo de verdad (authorization code + PKCE), con `resource` (RFC 8707) en la
    autorización y en el canje, como lo pide un cliente MCP."""
    navegador = con_sesion(usuario)
    verifier, challenge = pkce()
    extra = {"resource": resource} if resource else {}
    code = vuelta(consentir(navegador, peticion(challenge, scope=scope, **extra)))["code"]
    r = canjear(code, verifier, **extra)
    assert r.status_code == 200, r.content
    return r.json()["access_token"]


def mcp(
    metodo: str,
    params: dict | None = None,
    token: str | None = None,
    ruta: str = "/api/mcp",
    get=False,
    cabeceras: dict | None = None,
):
    """Una petición al servidor MCP como la manda un cliente (JSON-RPC sobre Streamable HTTP, 2026-07-28)."""

    async def ir():
        app = crear_aplicacion_mcp()
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url="http://testserver") as h:
            if get:
                return await h.get(ruta)
            cuerpo = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": metodo,
                "params": {
                    **(params or {}),
                    "_meta": {
                        "io.modelcontextprotocol/protocolVersion": VERSION,
                        "io.modelcontextprotocol/clientCapabilities": {},  # sin initialize: viajan en cada petición
                    },
                },
            }
            todas = {
                "Accept": "application/json, text/event-stream",
                "MCP-Protocol-Version": VERSION,
                "Mcp-Method": metodo,  # 2026-07-28: el método (y el nombre de la tool) también en cabeceras
                **({"Mcp-Name": params["name"]} if params and "name" in params else {}),
            }
            if token:
                todas["Authorization"] = f"Bearer {token}"
            return await h.post(ruta, json=cuerpo, headers={**todas, **(cabeceras or {})})

    return asyncio.run(ir())


@pytest.fixture
def cliente_cli(db):
    return registrar()  # gastos-cli, el cliente nativo del módulo 90 (público, con PKCE)


@pytest.fixture
def mundo():
    from asistente.tests.fakes.mundo import Mundo

    return Mundo()
