# asistente/application/ports/i_programador_de_compactacion.py — resumir DESPUÉS, fuera de la respuesta (módulo 99)
from abc import ABC, abstractmethod


class IProgramadorDeCompactacion(ABC):
    """Resumir una conversación es una llamada más al modelo: no se hace mientras la persona espera la respuesta, sino
    después (una tarea de Celery, cuando la respuesta ya está guardada)."""

    @abstractmethod
    def programar(self, usuario_id: int, hogar_id: int, conversacion_id: int) -> None: ...
