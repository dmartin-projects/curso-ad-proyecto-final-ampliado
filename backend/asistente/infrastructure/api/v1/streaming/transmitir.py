# asistente/infrastructure/api/v1/streaming/transmitir.py — de eventos del use case a Server-Sent Events (módulo 97)
"""event: tool
    data: {"nombre":"resumen_mes","texto":"Mirando el resumen del mes"}

    event: texto
    data: {"delta":"En septiembre gastasteis "}

    : latido                         ← un comentario, cada 15 s sin eventos

Un generador ASÍNCRONO: con ASGI, Django envía cada trozo en cuanto sale, y ninguna respuesta en curso ocupa un hilo
mientras espera (solo el use case, el tiempo que trabaja). Con un generador SÍNCRONO, Django lo consume ENTERO antes de
enviar nada (y avisa): la respuesta llegaría de golpe al final. Con WSGI, además, cada conversación abierta ocuparía un
worker de principio a fin.
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator, Callable

from asgiref.sync import sync_to_async

from asistente.infrastructure.api.v1.streaming.emisor_sse import EmisorSSE
from core.infrastructure.logging.request_id import request_id_var

logger = logging.getLogger(__name__)

LATIDO = 15.0  # segundos sin nada que enviar: los proxies (y los balanceadores) cortan las conexiones mudas
_FIN = object()


def evento(tipo: str, datos: dict) -> str:
    """Un evento SSE. El JSON en UNA línea: un salto de línea en `data` partiría el evento (json.dumps escribe los
    saltos de los textos como \\n)."""
    return f"event: {tipo}\ndata: {json.dumps(datos, ensure_ascii=False, default=str, separators=(',', ':'))}\n\n"


async def transmitir(trabajo: Callable[[EmisorSSE], object], *, latido: float = LATIDO) -> AsyncIterator[str]:
    """Ejecuta `trabajo(emisor)` en un hilo y devuelve sus eventos, en SSE, según llegan.

    Si la persona se va (cierra la pestaña, pulsa "Detener" y el navegador corta la petición), Django cancela este
    generador (CancelledError en el `await`): el `finally` lo marca en el emisor y el use case para en su siguiente paso,
    sin pagar más vueltas del modelo.
    """
    cola: asyncio.Queue = asyncio.Queue()
    bucle = asyncio.get_running_loop()
    emisor = EmisorSSE(bucle, cola)
    peticion = request_id_var.get()

    async def correr():
        try:
            # thread_sensitive=True: el mismo hilo que el resto del código síncrono de ESTA petición (Django le da uno
            # en ASGI): una sola conexión a la base de datos, que Django cierra al terminar
            await sync_to_async(trabajo, thread_sensitive=True)(emisor)
        except Exception:
            logger.exception("Error en la respuesta en streaming")
            emisor.emitir("error", {"detalle": "Ha ocurrido un error inesperado.", "request_id": peticion})
        finally:
            # Por el MISMO camino que los eventos (el bucle, en orden): detrás de los que el hilo ya haya enviado
            bucle.call_soon(cola.put_nowait, _FIN)

    tarea = asyncio.create_task(correr())
    try:
        while True:
            try:
                item = await asyncio.wait_for(cola.get(), timeout=latido)
            except TimeoutError:
                yield ": latido\n\n"
                continue
            if item is _FIN:
                break
            yield evento(*item)
    finally:
        emisor.cancelar()  # ha terminado, o la persona se ha ido: el trabajo no debe seguir
        if not tarea.done():
            logger.info("La persona se ha ido: se cancela la respuesta")
