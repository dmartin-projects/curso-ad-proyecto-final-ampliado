"""Módulo 97: de los eventos del use case (en un hilo) a Server-Sent Events (en el bucle de asyncio), sin Django."""

import asyncio
import json
import threading
import time

import pytest

from asistente.infrastructure.api.v1.streaming.transmitir import evento, transmitir


def test_un_evento_en_una_linea_de_datos():
    assert evento("texto", {"delta": "Hola\nadiós"}) == 'event: texto\ndata: {"delta":"Hola\\nadiós"}\n\n'


async def recoger(generador, n: int | None = None) -> list[str]:
    salida = []
    async for trozo in generador:
        salida.append(trozo)
        if n and len(salida) == n:
            break
    return salida


@pytest.mark.asyncio
async def test_los_eventos_en_orden_y_el_fin():
    def trabajo(emisor):
        for i in range(3):
            emisor.emitir("texto", {"delta": str(i)})

    trozos = await recoger(transmitir(trabajo))
    assert [json.loads(t.split("data: ")[1])["delta"] for t in trozos] == ["0", "1", "2"]


@pytest.mark.asyncio
async def test_un_latido_mientras_el_modelo_piensa():
    def trabajo(emisor):
        time.sleep(0.25)
        emisor.emitir("fin", {})

    trozos = await recoger(transmitir(trabajo, latido=0.1))
    assert trozos[0] == ": latido\n\n" and trozos[-1].startswith("event: fin")


@pytest.mark.asyncio
async def test_un_error_nuestro_llega_como_evento_sin_detalles():
    def trabajo(emisor):
        raise KeyError("detalle interno")

    (trozo,) = await recoger(transmitir(trabajo))
    assert trozo.startswith("event: error") and "detalle interno" not in trozo


@pytest.mark.asyncio
async def test_si_la_persona_se_va_el_trabajo_se_entera():
    parado = threading.Event()

    def trabajo(emisor):
        emisor.emitir("inicio", {})
        while not emisor.cancelado():  # como el use case: mira en cada paso
            time.sleep(0.01)
        parado.set()

    generador = transmitir(trabajo)
    assert (await recoger(generador, n=1))[0].startswith("event: inicio")
    await generador.aclose()  # lo que hace Django cuando el navegador cierra la conexión
    assert await asyncio.to_thread(parado.wait, 2)
