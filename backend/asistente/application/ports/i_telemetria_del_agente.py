# asistente/application/ports/i_telemetria_del_agente.py — medir el agente sin que el agente sepa con qué (módulo 98)
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractContextManager

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.resultado_agente import ResultadoAgente
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.resultado_tool import ResultadoTool


class ITelemetriaDelAgente(ABC):
    """Trazas y métricas de una pregunta y de cada tool. El bucle abre un `with` y, al terminar, dice cómo ha ido
    (llamando a lo que devuelve el `with`); el adapter de OpenTelemetry (infrastructure/telemetria) los convierte en
    spans y métricas con las convenciones GenAI. Las llamadas al modelo NO pasan por aquí: las mide un decorator del
    port ILLM (LLMMedido), que sabe del modelo lo que el bucle no sabe (el primer trozo, el que respondió de verdad).

    Context managers y no un par empezar/terminar: si algo lanza una excepción a mitad, el span se cierra igual (con
    el error), y el siguiente no queda colgando del anterior."""

    @abstractmethod
    def pregunta(self, contexto: ContextoPregunta) -> AbstractContextManager[Callable[[ResultadoAgente], None]]:
        """Una pregunta entera (todas sus vueltas)."""

    @abstractmethod
    def tool(self, llamada: LlamadaTool) -> AbstractContextManager[Callable[[ResultadoTool], None]]:
        """Una tool, desde que el modelo la pide hasta que su resultado está listo (también si se rechaza)."""
