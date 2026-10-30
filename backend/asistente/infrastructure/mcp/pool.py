# asistente/infrastructure/mcp/pool.py — un cliente MCP abierto por servidor, reutilizado (módulo 104)
"""El agente es síncrono (corre en un hilo del worker); el SDK de MCP, asíncrono. El pool tiene UN bucle de asyncio
en un hilo propio, y en él un `Client` abierto por servidor: la conexión HTTP (TLS, keep-alive) y la negociación del
protocolo se hacen una vez, no en cada llamada. Las llamadas llegan desde cualquier hilo con
`run_coroutine_threadsafe` y esperan su resultado con un tiempo máximo.

Si un cliente falla, se cierra y se olvida: la siguiente llamada abre otro.
"""

import asyncio
import threading
from collections.abc import Awaitable, Callable
from typing import Any

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client


class PoolMCP:
    def __init__(self, crear_http: Callable[[str, str], httpx2.AsyncClient] | None = None):
        """`crear_http(url, token)`: el cliente HTTP de cada servidor (en los tests, uno con un ASGITransport)."""
        self.crear_http = crear_http or _http
        self._clientes: dict[str, tuple[Client, httpx2.AsyncClient]] = {}
        self._bucle: asyncio.AbstractEventLoop | None = None
        self._cerrojo = threading.Lock()

    def ejecutar(self, url: str, token: str, operacion: Callable[[Client], Awaitable[Any]], timeout: float) -> Any:
        futuro = asyncio.run_coroutine_threadsafe(self._con_cliente(url, token, operacion), self._en_marcha())
        try:
            return futuro.result(timeout)
        except TimeoutError:
            futuro.cancel()
            raise

    def cerrar(self) -> None:
        if self._bucle is not None:
            asyncio.run_coroutine_threadsafe(self._cerrar_todos(), self._bucle).result(10)

    def _en_marcha(self) -> asyncio.AbstractEventLoop:
        with self._cerrojo:
            if self._bucle is None:
                self._bucle = asyncio.new_event_loop()
                threading.Thread(target=self._bucle.run_forever, name="pool-mcp", daemon=True).start()
            return self._bucle

    async def _con_cliente(self, url: str, token: str, operacion) -> Any:
        if url not in self._clientes:
            http = self.crear_http(url, token)
            cliente = Client(streamable_http_client(url, http_client=http))
            await cliente.__aenter__()  # negocia el protocolo (server/discover) una vez
            self._clientes[url] = (cliente, http)
        cliente, _ = self._clientes[url]
        try:
            return await operacion(cliente)
        except Exception:
            await self._cerrar(url)  # la siguiente, con un cliente nuevo
            raise

    async def _cerrar(self, url: str) -> None:
        cliente, http = self._clientes.pop(url, (None, None))
        if cliente is not None:
            try:
                await cliente.__aexit__(None, None, None)
            finally:
                await http.aclose()

    async def _cerrar_todos(self) -> None:
        for url in list(self._clientes):
            await self._cerrar(url)


def _http(url: str, token: str) -> httpx2.AsyncClient:
    return httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=httpx2.Timeout(10.0, connect=5.0))
