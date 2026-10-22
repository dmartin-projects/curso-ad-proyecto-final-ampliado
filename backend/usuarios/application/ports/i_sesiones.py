# usuarios/application/ports/i_sesiones.py (módulo 88)
from abc import ABC, abstractmethod


class ISesiones(ABC):
    @abstractmethod
    def cerrar_todas(self, usuario_id: int) -> None:
        """Invalida todos sus refresh tokens: las demás sesiones tendrán que volver a entrar."""
