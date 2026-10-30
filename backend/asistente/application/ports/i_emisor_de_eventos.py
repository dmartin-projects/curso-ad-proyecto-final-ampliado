# asistente/application/ports/i_emisor_de_eventos.py — por dónde salen los pasos de una respuesta (módulo 97)
from abc import ABC, abstractmethod
from typing import Any


class IEmisorDeEventos(ABC):
    """El use case cuenta lo que pasa ("consultando el resumen del mes", un trozo de texto, un gráfico…) y no sabe a
    quién: la vista de streaming los convierte en Server-Sent Events; un test los apunta en una lista."""

    @abstractmethod
    def emitir(self, tipo: str, datos: dict[str, Any]) -> None: ...

    @abstractmethod
    def cancelado(self) -> bool:
        """¿Se ha ido quien escuchaba (cerró la pestaña, pulsó "Detener")? Entonces no se sigue pagando al modelo."""
