"""Módulo 86: el WebSocket con el frontend en Vercel (otro origen que la API)."""

import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import override_settings

from config.asgi import application
from conftest import UsuarioFactory
from notificaciones.infrastructure.websocket.middleware import crear_ticket
from notificaciones.infrastructure.websocket.origenes import origen_permitido

PRODUCCION = "https://gastos.tudominio.com"
STAGING = "https://staging.gastos.tudominio.com"
VERCEL = override_settings(
    WS_ORIGENES=[PRODUCCION, STAGING], VERCEL_PREVIEW_PROYECTO="gastos", VERCEL_PREVIEW_EQUIPO="davids-projects"
)


@VERCEL
@pytest.mark.parametrize(
    "origen",
    [
        PRODUCCION,
        STAGING,
        "https://GASTOS.tudominio.com",  # el host no distingue mayúsculas
        "https://gastos-a1b2c3d4e-davids-projects.vercel.app",  # una preview de este proyecto
    ],
)
def test_origenes_permitidos(origen):
    assert origen_permitido(origen)


@VERCEL
@pytest.mark.parametrize(
    "origen",
    [
        "http://gastos.tudominio.com",  # sin TLS
        "https://gastos.tudominio.com:8443",  # otro puerto
        "https://gastos.tudominio.com.evil.example",  # un dominio que EMPIEZA igual
        "https://otro-a1b2c3d4e-davids-projects.vercel.app",  # otro proyecto del mismo equipo
        "https://gastos-a1b2c3d4e-otro-equipo.vercel.app",  # el mismo nombre de proyecto en otro equipo
        "https://gastos-a1b2c3d4e-x-davids-projects.vercel.app",  # un equipo "x-davids-projects"
        "https://gastos-a1b2c3d4e-davids-projects.vercel.app.evil.example",  # sufijo de más
        "https://gastos-a1b2c3d4ef-davids-projects.vercel.app",  # 10 caracteres: no es un hash de Vercel
        "https://gastos-a1b2c3d4e-davids-projectsXvercel.app",  # el "." de ".vercel.app", escapado
        "https://api.gastos.tudominio.com",  # la propia API: ya no es un origen de la app
    ],
)
def test_origenes_rechazados(origen):
    assert not origen_permitido(origen)


@override_settings(WS_ORIGENES=[], VERCEL_PREVIEW_PROYECTO="", VERCEL_PREVIEW_EQUIPO="")
def test_sin_configurar_no_hay_patron_de_previews():
    assert not origen_permitido("https://gastos-a1b2c3d4e-davids-projects.vercel.app")


async def _conectar(origen: bytes | None):
    usuario = await sync_to_async(UsuarioFactory)()
    ticket = await sync_to_async(crear_ticket)(usuario)
    cabeceras = [(b"origin", origen)] if origen else []
    ws = WebsocketCommunicator(application, f"/ws/notificaciones/?ticket={ticket}", headers=cabeceras)
    conectado, _ = await ws.connect()
    if conectado:
        assert (await ws.receive_json_from())["tipo"] == "conectado"
        await ws.disconnect()
    return conectado


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_el_websocket_acepta_vercel_y_rechaza_lo_demas():
    with VERCEL:
        assert await _conectar(PRODUCCION.encode())
        assert await _conectar(b"https://gastos-a1b2c3d4e-davids-projects.vercel.app")
        assert not await _conectar(b"https://gastos-a1b2c3d4e-otro-equipo.vercel.app")
        assert not await _conectar(b"http://testserver")  # configurado: ALLOWED_HOSTS ya no cuenta
        assert not await _conectar(None)  # sin Origin
    assert await _conectar(b"http://testserver")  # sin configurar: como antes (desarrollo, E2E)


@pytest.mark.django_db
def test_el_ticket_dice_donde_conectar(cliente, settings):
    c = cliente(UsuarioFactory())
    assert c.post("/api/v1/notificaciones/ws-ticket/").data["url"] is None  # desarrollo: el mismo host
    settings.WS_URL = "wss://api.gastos.tudominio.com/ws/notificaciones/"
    assert c.post("/api/v1/notificaciones/ws-ticket/").data["url"] == settings.WS_URL
