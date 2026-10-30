# asistente/application/agent/telemetria_muda.py — la telemetría por defecto: no mide nada (módulo 98)
from contextlib import contextmanager

from asistente.application.ports.i_telemetria_del_agente import ITelemetriaDelAgente


def _nada(_resultado) -> None:
    pass


class TelemetriaMuda(ITelemetriaDelAgente):
    """Null object, como ObservadorMudo: en los tests y en lo que no necesita medirse, el bucle no cambia."""

    @contextmanager
    def pregunta(self, contexto):
        yield _nada

    @contextmanager
    def tool(self, llamada):
        yield _nada
