# asistente/application/ports/i_avisos_de_progreso.py — cómo va un trabajo largo, a quien lo pidió (módulo 105)
from abc import ABC, abstractmethod


class IAvisosDeProgreso(ABC):
    """Lo implementa AvisosDeProgresoWS (el WebSocket de la app, módulo 76); en los tests, un fake que apunta."""

    @abstractmethod
    def avisar(self, usuario_id: int, hogar_id: int, tarea: str, datos: dict) -> None:
        """Nunca lanza: un aviso perdido no debe parar el trabajo."""
