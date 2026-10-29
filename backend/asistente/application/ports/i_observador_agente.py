# asistente/application/ports/i_observador_agente.py — quien quiere ver cada paso del agente (módulo 94)
from abc import ABC, abstractmethod

from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.domain.vo.resultado_tool import ResultadoTool


class IObservadorAgente(ABC):
    """El comando `preguntar` imprime cada paso; el chat (módulo 97) los manda al navegador por streaming; las
    métricas (módulo 98) los cuentan. El bucle no sabe quién escucha."""

    @abstractmethod
    def respuesta(self, respuesta: RespuestaLLM) -> None:
        """Un turno del modelo."""

    @abstractmethod
    def llamada(self, llamada: LlamadaTool) -> None:
        """Se va a ejecutar una tool."""

    @abstractmethod
    def resultado(self, resultado: ResultadoTool, duracion_ms: int) -> None:
        """Lo que la tool devuelve al modelo (o el error), y lo que ha tardado."""
