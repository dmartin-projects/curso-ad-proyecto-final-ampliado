# asistente/infrastructure/api/v1/streaming/emisor_sse.py — IEmisorDeEventos hacia una respuesta SSE (módulo 97)
import asyncio
import threading

from asistente.application.ports.i_emisor_de_eventos import IEmisorDeEventos


class EmisorSSE(IEmisorDeEventos):
    """El use case corre en un hilo (es síncrono: ORM, SDK del LLM); la respuesta, en el bucle de asyncio. `emitir` se
    llama desde el hilo, y una asyncio.Queue no es thread-safe: call_soon_threadsafe le pide al BUCLE que meta el
    evento en la cola, en su propio hilo y en orden. `cancelado` lo marca el bucle (la persona se ha ido) y lo mira el
    use case en cada paso."""

    def __init__(self, bucle: asyncio.AbstractEventLoop, cola: asyncio.Queue):
        self._bucle, self._cola = bucle, cola
        self._cancelado = threading.Event()

    def emitir(self, tipo: str, datos: dict) -> None:
        self._bucle.call_soon_threadsafe(self._cola.put_nowait, (tipo, datos))

    def cancelado(self) -> bool:
        return self._cancelado.is_set()

    def cancelar(self) -> None:
        self._cancelado.set()
