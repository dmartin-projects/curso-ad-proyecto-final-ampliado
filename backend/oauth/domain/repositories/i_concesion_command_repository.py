# oauth/domain/repositories/i_concesion_command_repository.py — el acceso dado a cada aplicación (ejercicio 1 del módulo 90)
from abc import ABC, abstractmethod


class IConcesionCommandRepository(ABC):
    """El acceso que un usuario ha dado a cada aplicación (sus refresh y access tokens vivos)."""

    @abstractmethod
    def tiene(self, usuario_id: int, client_id: str) -> bool: ...

    @abstractmethod
    def revocar(self, usuario_id: int, client_id: str) -> int:
        """Revoca todos sus tokens de esa aplicación (refresh, access, ID tokens). Cuántas sesiones había."""
